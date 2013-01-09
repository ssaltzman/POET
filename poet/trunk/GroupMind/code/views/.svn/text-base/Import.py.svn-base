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
import xml.dom.minidom
import gzip
import sys

class Import(BaseView.BaseView):

  NAME = 'Importer'

  def send_content(self, request):
    '''All cgi requests come through here.  This assumes that the headers have been sent
       and the output stream is ready'''
    # first check for the superuser
    if request.session.user.superuser != '1':
      request.writeln(HTML_HEAD + HTML_BODY)
      request.writeln("Error: You are not the superuser.  Please login again with the superuser username and password.")
      request.writeln("</body></html>")
      return

    request.writeln(request.cgi_multipart_form(action="importfile", rootid=request.getvalue('rootid', '')) + '''
      Import Data:
      <input type="file" name="filepath">
      <input type="submit" value="Import">
      </form>
    ''')

  def importfile_action(self,request):
    importfile = request.form['filepath']
    request.writeln(''' Import file: ''' + str(importfile) + ''' /n''')
    gz = gzip.GzipFile(importfile.filename, 'r', fileobj=importfile.file)
    doc = xml.dom.minidom.parse(gz)

    meetingnode = None
    usersnode = None
    for child in doc.documentElement.childNodes:
      if child.nodeName == 'MeetingData':
        meetingnode = child
      elif child.nodeName == 'UserData':
        usersnode = child
    assert meetingnode != usersnode != None, 'Error importing data.'

    data = datagate.import_xml(meetingnode)
    data.parentid = ''
    data.rewrite_ids()
    data.save(deep=1)
    item = datagate.get_item(request.getvalue('rootid', ''))
    item.insert_child(data)
    item.save()
