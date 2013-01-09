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
import datagate

class Debugger(BaseView):
  NAME = 'Debugger'


  def __init__(self):
      BaseView.__init__(self)
     
  def send_content(self, request):
    # first check for the superuser
    if request.session.user.superuser != '1':
      request.writeln(HTML_HEAD + HTML_BODY)
      request.writeln("Error: You are not the superuser.  Please login again with the superuser username and password.")
      request.writeln("</body></html>")
      return
      

  def send_content(self, request):
    '''Sends the content pane to the browser'''
    # switch to see if we want to send the frames or the content
    subview = request.getvalue('global_subview', '')
    if subview == 'datatree':
      self.send_data_tree(request)
      
    elif subview == 'eventswindow':
      self.send_eventswindow(request)
      
    else:
      self.send_frames(request)


  def send_frames(self, request):
    '''Sends the main debugger window frames'''
    request.writeln(HTML_HEAD + '''
      <script language='JavaScript' type='text/javascript'>
        function pad(n) {
          var s = "00" + n;
          return s.substring(s.length-2, s.length);
        }
        function prettyprint_arguments(args, depth) {
          if (args instanceof Array && args.length) {
            var formatted = [];
            for (var i = 0; i < args.length; i++) {
              formatted[i] = prettyprint_arguments(args[i], depth+1);
            }
            if (depth == 0) {
              return formatted.join(', ');
            }else{
              return '[' + formatted.join(', ') + ']';
            }
          }else if (args instanceof Array) {
            var formatted = [];
            for (key in args) {
              formatted[formatted.length] = prettyprint_arguments(key, depth+1) + ":" + prettyprint_arguments(args[key], depth+1);
            }
            if (depth == 0) {
              return formatted.join(', ');
            }else{
              return '{' + formatted.join(', ') + '}';
            }
          }else{
            return args;
          }
        }
        function showDebugEvent(etype, method, arguments, rowcolor) {
          var doc = top.gm_debug_eventswindow.document;
          var tbody = top.gm_debug_eventswindow.document.getElementById('eventstable');
          var tr = doc.createElement('tr');
          if (tbody.firstChild == null) {
            tbody.appendChild(tr);
          }else{
            tbody.insertBefore(tr, tbody.firstChild);
          }
          tr.setAttribute('bgColor', rowcolor);
          var td;
          var tt;
          var now = new Date();
          td = tr.appendChild(doc.createElement('td'));
          tt = td.appendChild(doc.createElement('tt'));
          tt.appendChild(doc.createTextNode(now.getHours() + ":" + pad(now.getMinutes()) + ":" + pad(now.getSeconds())));
          td = tr.appendChild(doc.createElement('td'));
          tt = td.appendChild(doc.createElement('tt'));
          tt.appendChild(doc.createTextNode(etype));
          td = tr.appendChild(doc.createElement('td'));
          tt = td.appendChild(doc.createElement('tt'));
          tt.appendChild(doc.createTextNode(method));
          td = tr.appendChild(doc.createElement('td'));
          tt = td.appendChild(doc.createElement('tt'));
          tt.appendChild(doc.createTextNode(prettyprint_arguments(arguments, 0)));
        }
      </script>      
    ''')
    debugview = request.getvalue('debugview', '')
    if debugview:
      request.writeln('<frameset rows="* ,150, 25">')
      request.writeln('<frame name="gm_debug_realview" marginheight=0 marginwidth=0 src="' + request.cgi_href(debugview=debugview, global_view=debugview) + '">')
    else:
      request.writeln('<frameset rows="50%,*">')
    request.writeln('<frame name="gm_debug_eventswindow" marginheight=0 marginwidth=0  src="' + request.cgi_href(global_subview='eventswindow') + '">')
    request.writeln('<frame name="gm_debug_datatree" marginheight=0 marginwidth=0 src="' + request.cgi_href(global_subview='datatree') + '">')
    request.writeln('</frameset>')
    request.writeln('</html>')
    

  #######################################################
  ###   Data tree (views the data tree)
    
  def send_data_tree(self, request):
    '''Sends the data tree'''
    root = datagate.get_item(request.getvalue('global_rootid', 'z'))
    try:
      maxdepth = int(request.getvalue('maxdepth', '15'))
    except ValueError:
      maxdepth = 15
      
    request.writeln('<html><body bgcolor="#CCCCFF">')
    request.writeln(request.cgi_form(global_rootid=None))
    request.writeln('''
      <center>
      <table border=1 cellpadding=10 cellspacing=0>
        <tr>
          <td>
            First Item ID: <input type="text" size="30" name="global_rootid" value="''' + request.getvalue('global_rootid', 'z') + '''">
            ("z" for top)
          </td><td>
            Maximum Depth: <input type="text" size="4" name="maxdepth" value="''' + request.getvalue('maxdepth', str(maxdepth)) + '''">
          </td><td>
            <input type="submit" value="Refresh">
          </td>
        </tr>
      </table>
      </center>
    ''')
    request.writeln('<ul>')
    self.recurse(request, root.get_child_items(), maxdepth)    
    request.writeln('</ul>')
    request.writeln("</body></html>")
    
    
  def recurse(self, request, items, depth):
    if depth == 0:
      return
    for item in items:
      encoded = ''
      for key in item.__dict__.keys():
        if not key in ['childids', 'parentid', 'id'] and key[:10] != 'groupright':
          encoded += '&' + encode(key) + '=' + encode(str(getattr(item, key))[:100])
      encoded += '&id=' + item.id
      request.write('<li>')
      request.write(encoded)
      children = item.get_child_items()
      if len(children) > 0:
        request.writeln()
        request.writeln('<ul>')
        self.recurse(request, children, depth - 1)
        request.writeln('</ul>')
      request.writeln('</li>')
      
      
  ##########################################################
  ###   Events window (views events passed to the program)
      
  def send_eventswindow(self, request):
    '''Sends the events view frame'''
    request.writeln('''
      <html><body bgcolor="#FFFFFF">
      <table border=1 cellpadding=2 cellspacing=1 width="100%">
        <tbody>
          <tr bgcolor="9999CC">
            <th>Time</th>
            <th>Type</th>
            <th>Method</th>
            <th>Arguments</th>
          </tr>
        </tbody>
        <tbody id="eventstable">
        </tbody>
      </table>
      </body></html>
    ''')
    
    
    