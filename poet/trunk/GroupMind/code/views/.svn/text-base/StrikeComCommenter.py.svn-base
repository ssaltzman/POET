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

import BaseView
from Constants import *
import datagate

class StrikeComCommenter(BaseView.BaseView):
  NAME = 'StrikeComCommenter'
  TOP_LEVEL_COMPONENT = 1
  REGULAR_COMPONENT = 1 
  
  rights_list = [ 'View Author', 'View Comments', 'Add', 'Edit', 'Delete' ]

  def __init__(self):
    BaseView.BaseView.__init__(self)
    self.interactive = 1
    
    
  def send_content(self, request):
    '''Sends the content pane to the browser'''
    # switch to see if we want to send the frames or the content
    subview = request.getvalue('subview', '')
    if subview == 'content':
      self.send_initial_content(request)
      
    elif subview == 'inputframe':
      self.send_input(request)
      
    elif subview == 'editform':
      self.send_editform(request)
    
    else:
      self.send_frames(request)
    

  def send_frames(self, request):
    '''Sends the main two frames, including the event handlers'''
    # determine if this meeting is anonymous or not
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    item = root.search1(name="comments")
    rights = self.get_user_rights(request)
    request.writeln('''
      <html>
      <head>
      <title>Content frames</title>
      <script language='JavaScript' type='text/javascript'>
      <!--
        function editItem(itemid) {
          inputframe.location.replace("''' + request.cgi_href(subview='editform', itemid=None) + '''&itemid=" + itemid);
        }
        
        function processAdd(itemid, itemtext, creatorname, creatoremail) {
    ''')
    if rights['View Comments']: # View Comments at all
      request.writeln('''
          // create the table and add to the body
          // I create the table tag manually so I can append it into the body directly
          var body = output.document.getElementById('outputBody');
          var table = output.document.createElement("table");
      ''')
      if item.getvalue('commenterdirection', '') == 'newest':
        request.writeln('''
          // find the first table object
          var temp = body.firstChild;
          while (temp != null && temp.nodeName != "TABLE") {
            temp = temp.nextSibling;
          }
          if (temp != null) {
            body.insertBefore(table, temp)
          }else{
            body.appendChild(table);
          }
        ''')
      else:
        request.writeln('''
          body.appendChild(table);
        ''')
      request.writeln('''
          table.id = itemid;
          table.border = 0;
          table.cellspacing = 0;
          table.cellpadding = 0;
          table.width = "100%";
          var tbody = table.appendChild(output.document.createElement("tbody"));
          var tr = tbody.appendChild(output.document.createElement("tr"));
          var td = null;
          var a = null;
          var img = null;
          var span = null;
          
          td = tr.appendChild(output.document.createElement("td"));
          td.vAlign = "top";
          td.align = "left";
      ''')
      
    # edit right
    if rights['View Comments'] and rights['Edit']:
      request.writeln('''
          // the edit link
          a = td.appendChild(output.document.createElement("a"));
          a.href = "javascript:parent.editItem('" + itemid + "');";
          img = a.appendChild(output.document.createElement("img"));
          img.border = "0";
          img.src = "''' + join(WEB_PROGRAM_URL, 'icon-edit.png') + '''";
          img.alt = "Edit";
          td.appendChild(output.document.createTextNode(" "));
      ''')

    # delete right
    if rights['View Comments'] and rights['Delete']:  
      request.writeln('''  
          // the delete link
          a = td.appendChild(output.document.createElement("a"));
          a.href = "javascript:confirm_target_url('Delete this item?', getEvents(), \'''' + request.cgi_href(frame='events', gm_action='delete_comment', itemid=None) + '''&itemid=" + itemid + "');";
          img = a.appendChild(output.document.createElement("img"));
          img.border = "0";
          img.src = "''' + join(WEB_PROGRAM_URL, 'icon-delete.png') + '''";
          img.alt = "Delete";
          td.appendChild(output.document.createTextNode(" "));
      ''')
      
      
    # text of the comment
    if rights['View Comments']:
      request.writeln('''
          // the text cell
          span = td.appendChild(output.document.createElement('span'));
          span.id = "text" + itemid;
          span.appendChild(output.document.createTextNode(itemtext));
          span.style.color = "#666633";
      ''')
      
    # comment author
    if rights['View Comments'] and rights['View Author']:
      request.writeln('''      
          // the username/email link
          td = tr.appendChild(output.document.createElement("td"));
          td.noWrap = true;
          td.align = "right";
          td.vAlign = "top"
          a = td.appendChild(output.document.createElement("a"));
          a.href = "mailto:" + creatoremail;
          a.appendChild(output.document.createTextNode(creatorname));
          a.style.color = "#666633";
          td.appendChild(output.document.createTextNode(" "));
      ''')
        
    # end the processAdd function      
    request.writeln('''
        }
    ''')

    # processRemove and processEdit functions
    request.writeln('''    
        function processDelete(itemid) {
          var body = output.document.getElementById('outputBody');
          body.removeChild(output.document.getElementById(itemid));
        }
        
        function processEdit(itemid, itemtext) {
          // change the text
          var span = output.document.getElementById("text" + itemid);
          for (var i = 0; i < span.childNodes.length; i++) {
            if (span.childNodes[i].nodeType == 3) { // IE doesn't recognize the TEXT_NODE constant
              span.removeChild(span.childNodes[i]);
              span.appendChild(output.document.createTextNode(itemtext));
              break;
            } 
          }
          
          // update the rating
          //var span = output.document.getElementById("ratingSpan" + itemid);
          //if (span) {
          //  processRatings(item, span, output.document);
          //}
        }
       
      //-->
      </script>
      </head>
      <frameset border='0' rows="*,100">
        <frame name='output' marginheight='0' marginwidth='0' src=\'''' + request.cgi_href(subview='content') + '''\'>
        <frame name='inputframe' marginheight='0' marginwidth='0'  src=\'''' + request.cgi_href(subview='inputframe') + '''\'>
      </frameset>
      </html>
    ''')
    
    
  def send_initial_content(self, request):
    '''Sends the initial content frame to the browser'''
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    item = root.search1(name="comments")

    request.writeln(HTML_HEAD + '<body bgcolor="#C3C191" id="outputBody" bottommargin="4" topmargin="4" leftmargin="4" rightmargin="4" onload="getEvents().refreshEvents()" style="background-image:url(/strikecom/blue-right.png); background-repeat: no-repeat;">')
    request.writeln('<div>&nbsp;</div>')
    request.writeln('</body></html>')
    
    
  def send_input(self, request):
    '''Sends the input frame, where users can submit new comments'''
    rights = self.get_user_rights(request)
    onload = ''
    if request.getvalue('initial_load', '1') != '1':  # after the first initial_load, we tell the events to refresh because it means we just submitted something
      onload = ' onload="getEvents().refreshEvents()"'
    request.writeln(
      HTML_HEAD + '''<body bgcolor="#C3C191" topmargin="8"''' + onload + '''>
    ''')
    
    if rights['Add']: # add right
      request.writeln(request.cgi_form(parentid=request.getvalue('global_rootid',''), initial_load='0', gm_action='add_comment', previousid=None, text=None) + '''
      <div align="center"><textarea name="text" cols="50" rows="2" style="width:80%"></textarea></div>
      <div align="center"><input type="submit" name="submit" value="Add"> <input type="reset" name="submit" value="Clear"></div>
      </form>
      ''')
    request.writeln('''
      </body>
      </html>
    ''')
    
    
  def send_editform(self, request):
    '''Sends the input frame for editing of an item'''
    item = datagate.get_item(request.getvalue('itemid', ''))
    request.writeln(
      HTML_HEAD + '''<body bgcolor="#C3C191" topmargin="8">
      <center>
      ''' + request.cgi_form(subview='inputframe', initial_load='0', text=None, gm_action='edit_comment', itemid=item.id) + '''
      <textarea name="text" cols="50" rows="2" style="width:80%">''' + item.text + '''</textarea>
      <br>
      <input type="submit" name="submit" value="Submit Changes">
      <input type="submit" name="submit" value="Cancel Changes">
      </form>
      </center>
      </body>
      </html>
    ''')


  def get_user_rights(self, request):
    '''Retrieves the static user rights for a strike com chat'''
    rights = dict([ (right, False) for right in self.rights_list ])
    rights['View Author'] = True
    rights['View Comments'] = True
    rights['Add'] = True
    return rights


  ###################################
  ###   Actions

  def get_initial_events(self, request, rootid):
    '''Retrieves a list of initial javascript calls that should be sent to the client
       when the view first loads.  Typically, this is a series of add_processor
       events.'''
    events = []
    root = datagate.get_item(rootid)
    comments = root.search1(name="comments")
    for item in comments.get_child_items():
      creator = datagate.get_item(item.creatorid)
      events.append('processAdd("%s","%s","%s","%s")' % (item.id, item.text, creator.name, creator.email))
    return events
    
  
  def _create_add_event(self, item):
    creator = datagate.get_item(item.creatorid)
    return 'processAdd("%s","%s","%s","%s")' % (item.id, item.text, creator.name, creator.email)


  def add_comment_action(self, request):
    '''Responds to an add from the browser.'''
    # create the new item
    creator = request.session.user
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    comments = root.search1(name="comments")
    item = datagate.create_item(creatorid=creator.id, parentid=comments.id)
    item.text = request.getvalue('text', '')
    item.save()
    
    # return a new event
    return [ self._create_add_event(item) ]


  def edit_comment_action(self, request):
    '''Responds to an edit event from the browser.'''
    if request.getvalue('submit', '') != 'Submit Changes':
      return
      
    # perform the action
    item = datagate.get_item(request.getvalue('itemid', ''))
    item.text = request.getvalue('text', '')
    item.save()
    
    # return an edit event
    return [ 'processEdit("%s","%s")' % (item.id, item.text) ]
    
    
  def delete_comment_action(self, request):
    '''Responds to a delete event from the browser'''
    datagate.del_item(request.getvalue('itemid', ''))
    return [ 'processDelete("%s")' % request.getvalue('itemid', '') ]
    
    
  def get_data_items(self, request):
    '''Retrieves the data items for this view.'''
    return datagate.get_child_items(request.getvalue('global_rootid', ''))

  
  ################################
  ###   Administrator methods


  def initialize_activity(self, request, new_activity):
    '''Called from the Administrator.  Sets up the activity'''
    BaseView.BaseView.initialize_activity(self, request, new_activity)
    comments = datagate.create_item(creatorid=request.session.user.id, parentid=new_activity.id)
    comments.name = 'comments'
    comments.save()
    

  def send_admin_page(self, request):
    '''Sends an administrator page for this view.'''
    BaseView.BaseView.send_admin_page(self, request)
    activity = datagate.get_item(request.getvalue('itemid', ''))
    
    request.writeln(request.cgi_form(gm_action='Commenter.savetitle', title=None, direction=None))
    request.writeln('''
      <p>
      <center>
      Title (html is permitted): <input type=text size=40 name=title value="''' + html(activity.getvalue('commentertitle', '')) + '''">
      <p>
      Newest First: <input type=radio name=direction value="newest" ''' + (activity.getvalue('commenterdirection', '') == 'newest' and ' checked' or '') + '''>
      <br>
      Oldest First: <input type=radio name=direction value="oldest" ''' + (activity.getvalue('commenterdirection', 'oldest') == 'oldest' and ' checked' or '') + '''>
      <p>
      <input type=submit value="Save">
      </center>
      </form>
    ''')

  def savetitle_action(self, request):
    activity = datagate.get_item(request.getvalue('itemid', ''))
    activity.commentertitle = request.getvalue('title', '')
    activity.commenterdirection = request.getvalue('direction', 'oldest')
    activity.save()
    
