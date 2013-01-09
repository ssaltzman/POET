#!/usr/bin/python

####################################################################################
#                                                                                  #
# Copyright (c) 2003 Dr. Conan C. Albrecht                                         #
#                                                                                  #
# This file is part of GroupMind.                                                  #
#                                                                                  #
# GroupMind is free software; you can redistribute it and/or modify                #
# it under the terms of the GNU General Public License as published by             #
# the Free Software Foundation; either version 2 of the License, or                # 
# (at your option) any later version.                                              #
#                                                                                  #
# GroupMind is distributed in the hope that it will be useful,                     #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                   #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                    #
# GNU General Public License for more details.                                     #
#                                                                                  #
# You should have received a copy of the GNU General Public License                #
# along with Foobar; if not, write to the Free Software                            #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA        #
#                                                                                  #
####################################################################################

from BaseView import BaseView
from Constants import *
import Directory
import time

class Sessions(BaseView):
  NAME = 'Sessions'

  def __init__(self):
      BaseView.__init__(self)
     
  def send_content(self, request):
    if request.session.user.superuser != '1':
      request.writeln(HTML_HEAD + HTML_BODY)
      request.writeln('Error: You must be superuser to view active sessions.')
      request.writeln('</body></html>')
      return
      
    request.writeln(HTML_HEAD + HTML_BODY)
    request.writeln('<h1>Current sessions:</h1>')    
    request.writeln('<p>')
    request.writeln('<a href="' + request.cgi_href() + '">Refresh</a>')
    request.writeln('|')
    request.writeln('<a href="' + request.cgi_href(gm_action="clearall") + '">Clear All</a>')
    request.writeln('</p>')
    request.writeln('<table border=1 cellspacing=0 cellpadding=3>')
    request.writeln('<tr>')
    request.writeln('<th>Username</th>')
    request.writeln('<th>Started</th>')
    request.writeln('<th>Minutes</th>')
    request.writeln('<th>Actions</th>')
    request.writeln('</tr>')
    sessions = Directory.sessions.values()
    sessions.sort(lambda a,b: cmp(a.user.username, b.user.username))
    now = time.time()
    for session in sessions:
      request.writeln('<tr>')
      request.writeln('<td>' + session.user.username + '</td>')
      request.writeln('<td>' + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(session.started)) + '</td>')
      request.writeln('<td>' + str(round((now - session.started) / 60, 1)) + '</td>')
      if session == request.session:
        request.writeln('<td>(your session)</td>')
      else:
        request.writeln('<td><a href="' + request.cgi_href(gm_action='clearsession', sessionid=session.id) + '">Clear</a></td>')
      request.writeln('</tr>')
    request.writeln('</table>')
    request.writeln("</body></html>")
    
    
  def clearsession_action(self, request):
    session = Directory.get_session(request.getvalue('sessionid'))
    Directory.logout(session)
    
  
  def clearall_action(self, request):
    for session in Directory.sessions.values():
      if session != request.session:
        Directory.logout(session)
        