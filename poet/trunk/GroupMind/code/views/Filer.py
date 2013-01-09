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
#
#  Serves files directly from the items tree.  This is good for disk use because
#  all image bytes are right in the item.  The drawback is large images will
#  be inefficient.  The items tree should handle it fine, but it's probably not
#  the best method for large files.
#
#  This upload procedure supports uploading one file at a time, and it puts a single
#  file into an item.  Use multiple items for multiple files.
#
#  The file bytes are stored in item.filebytes
#  The file type (mime type sent by browser) is stored in item.filetype
#  The file name is stored in item.filename

from BaseView import BaseView
from Constants import *
import datagate

class Filer(BaseView):
  NAME = 'Filer'

  def __init__(self):
      BaseView.__init__(self)
     
  def send_content(self, request):
    if request.getvalue('subview', '') == 'upload': # an example form
      self.send_upload_form(request)
    else:
      self.send_file_bytes(request)
      

  def send_upload_form(self, request):
    '''An example form to upload files.'''
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    request.writeln(HTML_HEAD + HTML_BODY)

    # show the existing graphic (we assume it is a graphic for example purposes, but it could be anything)
    if hasattr(root, 'filebytes'):
      request.writeln('''
        <div align="center">&nbsp;</div>
        <div align="center">
          <img src="''' + request.cgi_href(view="Filer", gm_contenttype=encode(root.filetype), subview=None, file=None) + '''" border=0>
        </div>
        <div align="center">&nbsp;</div>
      ''')

    # upload form
    # I use an _ for the name of the control so it doesn't get passed around to other forms
    request.writeln(request.cgi_multipart_form(gm_action="uploadfile", file=None) + '''
      <div align="center">
      Upload new image:
      <input type="file" name="_file">
      <input type="submit" value="Upload">
      </form>
      </div>
    ''')
    request.writeln("</body></html>")


  def send_file_bytes(self, request): 
    '''Sends the file bytes to the browser'''
    # to send a file, the default contenttype sent by the program must be overridden.  See the
    # <img> link above for an example.
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    request.write(root.filebytes)
    
    
    
  #######################################################
  ###   Actions
  
  def uploadfile_action(self, request):
    '''Uploads a file directly into the items tree'''
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    if request.form.has_key('_file'):
      fileitem = request.form['_file']
      root.filebytes = fileitem.file.read()
      root.filetype = fileitem.type
      root.filename = fileitem.filename
      root.save()
      