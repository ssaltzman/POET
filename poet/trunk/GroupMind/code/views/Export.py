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

from Constants import *
import BaseView
import Directory
import datagate
import StringIO
import gzip
import sys

class Export(BaseView.BaseView):
  '''Exports the item tree to XML, starting with request.getvalue('global_rootid').
     The xml is automatically gzipped because 1) it gives nice compression, and
     2) the gzip mime type tells most browsers to open the "save as" dialog.
  '''

  NAME = 'Exporter'

  def send_content(self, request):
    '''All cgi requests come through here.  This assumes that the headers have been sent
       and the output stream is ready'''
    # first check for the superuser
    if request.session.user.superuser != '1':
      request.writeln(HTML_HEAD + HTML_BODY)
      request.writeln("Error: You are not the superuser.  Please login again with the superuser username and password.")
      request.writeln("</body></html>")
      return
      
       # export the meeting
    doc = Directory.export_meeting(request.getvalue('global_rootid', ''))
      
    # gzip it to a stringio object and write to the response
    zipped = StringIO.StringIO()
    gz = gzip.GzipFile(mode='w', fileobj=zipped)
    gz.write(doc.toxml())
    gz.close()
    request.write(zipped.getvalue())
    zipped.close()

        
