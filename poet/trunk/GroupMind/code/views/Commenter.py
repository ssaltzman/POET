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
from Events import Event
import Directory
import datagate
import time, datetime

class Commenter(BaseView.BaseView):
  NAME = 'Commenter'
  BODY_TAG_NO_CLOSE = HTML_BODY_NO_CLOSE  # allows subclasses to customize this
  
  def __init__(self):
    BaseView.BaseView.__init__(self)
    self.interactive = 1
    
    
  def send_content(self, request):
    '''Sends the content pane to the browser'''
    request.writeln(HTML_HEAD_NO_CLOSE + '<link type="text/css" rel="stylesheet" href="' + join(WEB_PROGRAM_URL, "layout.css") + '" />')
    
    request.writeln('''<script src="''' + join(WEB_PROGRAM_URL, 'jquery-1.4.2.min.js') + '''"></script>''')
    request.writeln('''<script src="''' + join(WEB_PROGRAM_URL, 'jquery-ui-1.8.2.custom.min.js') + '''"></script>''')
    request.writeln('''<link href="''' + join(WEB_PROGRAM_URL, 'jquery-ui-1.8.2.custom.css') + '''" rel="stylesheet" type="text/css"/>''')
    
    self.send_javascript(request)
    
    request.writeln('''
      <script language='JavaScript' type='text/javascript'>
        $(document).ready(function() {
	  $("input:button").button();
	  $("input:submit").button();
	  $("button").button();
	});
        </script>
    ''')
    
    
    request.writeln("</head>")

    request.writeln(self.BODY_TAG_NO_CLOSE + ' id="outputBody">')
    
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    item = root.search1(name="comments")
        
    activity = Directory.get_meeting(request.getvalue('global_rootid', ''))
    activities = activity.get_parent()
    meeting = activities.get_parent()
    user_is_pm = False
    for child in meeting:
     if child.name == "groups":
       for group in child:
         if group.name == "PM":
           for pm_item in group:
             if pm_item.user_id == request.session.user.id:
               user_is_pm = True
               
    if request.session.user.superuser == '1' or user_is_pm:
      request.writeln('<div><table cellspacing="0" style="border-bottom:#99ccff 1px dotted;padding:3px;" width=100%><tr>')
      request.writeln('''<td id="menu-logo">
      			<div id="poet-logo">POET</a>
                       </td>''')

      request.writeln('<td id="user-menu">')
      request.writeln('logged in as <strong>'+request.session.user.name+'</strong>')
  
    #navigation
      if request.session.user.superuser == '1':
        request.writeln('<span class="divider">|</span> <a href="' + request.cgi_href(_adminaction=None, global_adminview=None) + '">Home</a>')
      request.writeln('  <span class="divider">|</span> <a target="_top" href="' + request.cgi_href(itemid=meeting.id, global_view='Administrator', global_adminview='POET') + '">Manage Program</a>')
      request.writeln('''<span class="divider">|</span> <a onclick='javascript:openProgInfo();'>Program Information</a> <span class="divider">|</span> <a onclick='javascript:openHelp();'>Help</a> <span class="divider">|</span> ''')
      request.writeln('<a href="' + request.cgi_href(global_view='login', _adminaction='logout') + '">Logout</a>')
      request.writeln('</td>')
      request.writeln('</tr></table></div>')
      
    request.writeln("<br/><h2 align='center'>Brainstorming</h2>")
    
    if item.getvalue('commentertitle', '') != '':
      request.writeln('<p id="title"><h3>' + item.getvalue('commentertitle', '') + '</h3><h4>' + item.getvalue('commenterdescrip', '') + '</h4></p>')
      
    request.writeln('''<div id='addIdea'>
		      <button align='right' onclick='document.getElementById("addcomment").style.display="block";'>Add</button>
		      <div id='addcomment' style='display:none;' align='center'>
		      ''' + request.cgi_form(gm_action="add_comment") + '''
			  <textarea align='center' name="text" cols="50" rows="2" style="width:80%"></textarea>
			  <input type="submit" value="Add" name="submit">
			</form>
		      </div>
		    </div> 
    ''')
    
    request.writeln('''<br/><div id='commentDiv' class='commentList'></div>''')
    
    request.writeln('''<script language='JavaScript' type='text/javascript'>
                    parent.startEventLoop();
                    </script>
    ''')
    
    request.writeln('</body></html>')
    
    
  def send_javascript(self, request):
    '''Sends the javascript to the client.  This is called from send_frames and is
       separated to its own method to allow subclasses to add their own Javascript.'''
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    item = root.search1(name="comments")
    rights = self.get_user_rights(request)

    request.writeln('''
      <script language='JavaScript' type='text/javascript'>
        // the images for the ten-point rating scale        
        
        function editItem(itemid) {
          inputframe.location.replace("''' + request.cgi_href(subview='send_editform', itemid=None) + '''&itemid=" + itemid);
        }
        
        function openHelp() {
          window.open("''' + WEB_PROGRAM_URL + '''/Help/", "helpwindow", "dependent,height=800,width=1000,scrollbars,resizable");
          return false;
        }
	
	function openProgInfo() {
          window.open("''' + WEB_PROGRAM_URL + '''/ProgInfo/", "proginfowindow", "dependent,height=800,width=1000,scrollbars,resizable");
          return false;
        }
        
        function processAdd(itemid, itemtext, itemtime, creatorid, creatorname, creatoremail, subitems) {
    ''')
    
    request.writeln('''
	var allComments = document.getElementById('commentDiv');
	var comment = allComments.appendChild(document.createElement("div"));
	comment.className = "comment";
	var table = comment.appendChild(document.createElement("table"));
	var tr = table.appendChild(document.createElement("tr"));
	var icons = tr.appendChild(document.createElement("td"));
	var idea = tr.appendChild(document.createElement("td"));	
	var creator = tr.appendChild(document.createElement("td"));
	  
    ''')
    
    #create hidden tr for adding subideas
    request.writeln('''
      var addtr = table.appendChild(document.createElement("tr"));
      addtr.className = "commentBody" + itemid;
      $(".commentBody" + itemid).hide();
      var addtext = addtr.appendChild(document.createElement("td"));
      addtext.colSpan = "3";
      addtext.vAlign = "middle";
      addtext.align = "center";
      /*
      var form = addtext.appendChild(''' + request.cgi_form(gm_action="add_sub_comment", itemid=None) + '''&itemid=" + itemid);
      var textarea = form.appendChild(document.createElement("textarea"));
      textarea.name = "text";
      textarea.style.width = "80%";
      textarea.cols = '50';
      textarea.rows = '2';
      
      form.appendChild(document.createTextNode(" "));
      
      var submitBut = form.appendChild(document.createElement("input"));
      submitBut.type = "submit";
      submitBut.value = "Add";
      */
    ''')
    
    #input the icons
    request.writeln('''
	icons.align= "left";
	icons.noWrap = true;
	var add = icons.appendChild(document.createElement("a"));
	add.className = "commentHead" + itemid;
	$('.commentHead' + itemid).click(function() { $('.commentBody' + itemid).show(); } );
	var addicon = add.appendChild(document.createElement('span'));
	addicon.className = "ui-icon ui-icon-plusthick";
	addicon.appendChild(document.createTextNode(" "));

	var edit = icons.appendChild(document.createElement("a"));
	edit.href = "javascript:parent.editItem('" + itemid + "');"; 
	var editicon = edit.appendChild(document.createElement('span'));
	editicon.className = "ui-icon ui-icon-pencil";
	editicon.appendChild(document.createTextNode(" "));
	
	var de = icons.appendChild(document.createElement("a"));
	de.href = "javascript:parent.confirmDelete('" + itemid + "');"; 
	var deicon = de.appendChild(document.createElement('span'));
	deicon.className = "ui-icon ui-icon-closethick";
    ''')
    
    #input the text
    request.writeln('''
	idea.align= "left";
	idea.noWrap = true;
	var ideatext = idea.appendChild(document.createElement('span'));
	ideatext.id = "text" + itemid;
	ideatext.appendChild(document.createTextNode(itemtext));
	
	idea.appendChild(document.createTextNode(" "));
	
	var posted = idea.appendChild(document.createElement('span'));
	posted.style.fontStyle = "italic";
	posted.style.fontSize = "11";
	posted.style.color = "#bbb";

	var currenttime = ''' + str(time.time()) + ''';
	var postedTimeElapsed = currenttime - itemtime;
	var postedTimeInterval = Math.round(postedTimeElapsed) + " seconds";

	if(postedTimeElapsed > 86400){
	  postedTimeInterval = Math.round(postedTimeElapsed/86400) + " days";
	}
	else if(postedTimeElapsed > 3600){
	  postedTimeInterval = Math.round(postedTimeElapsed/3600) + " hours";
	}
	else if (postedTimeElapsed > 60){
	  postedTimeInterval = Math.round(postedTimeElapsed/60) + " minutes";
	}

	posted.appendChild(document.createTextNode("posted " + postedTimeInterval + " ago"));
	var currenttime = ''' + str(time.time()) + ''';
    ''')
    
    #input the creator
    request.writeln('''
	creator.align = "right";
	creator.noWrap = true;
	var email = creator.appendChild(document.createElement("a"));
	email.href = "mailto:" + creatoremail;
	email.appendChild(document.createTextNode(creatorname));
	creator.appendChild(document.createTextNode(" "));	    
    ''')
    
    #for each subitem create subTR
    request.writeln('''
	for(var i = 0; i < subitems.length; i++){
	  var subTR = table.appendChild(document.createElement("tr"));
	  var indent = subTR.appendChild(document.createElement("td"));
	  indent.appendChild(document.createTextNode(" " ));
	  var subicons = subTR.appendChild(document.createElement("td"));
	  var subidea = subTR.appendChild(document.createElement("td"));	
	  var subcreator = subTR.appendChild(document.createElement("td"));
	  
	  subicons.align= "left";
	  subicons.noWrap = true;
	  var add = subicons.appendChild(document.createElement("a"));
	  add.className = "commentHead";
	  var addicon = add.appendChild(document.createElement('span'));
	  addicon.className = "ui-icon ui-icon-plusthick";
	  addicon.appendChild(document.createTextNode(" "));
    
	  var edit = subicons.appendChild(document.createElement("a"));
	  edit.href = "javascript:parent.editItem('" + itemid + "');"; 
	  var editicon = edit.appendChild(document.createElement('span'));
	  editicon.className = "ui-icon ui-icon-pencil";
	  editicon.appendChild(document.createTextNode(" "));
	  
	  var de = subicons.appendChild(document.createElement("a"));
	  de.href = "javascript:parent.confirmDelete('" + itemid + "');"; 
	  var deicon = de.appendChild(document.createElement('span'));
	  deicon.className = "ui-icon ui-icon-closethick";
	  deicon.appendChild(document.createTextNode(" "));
	  
	  subidea.align= "left";
	  subidea.noWrap = true;
	  var ideatext = subidea.appendChild(document.createElement('span'));
	  ideatext.id = "text" + itemid;
	  ideatext.appendChild(document.createTextNode(itemtext));
	  
	  idea.appendChild(document.createTextNode(" "));
	  
	  var posted = idea.appendChild(document.createElement('span'));
	  posted.style.fontStyle = "italic";
	  posted.style.fontSize = "11";
	  posted.style.color = "#bbb";
	  posted.appendChild(document.createTextNode("posted 2 hours ago"));
	  
	  subcreator.align = "right";
	  subcreator.noWrap = true;
	  var email = subcreator.appendChild(document.createElement("a"));
	  email.href = "mailto:" + creatoremail;
	  email.appendChild(document.createTextNode(creatorname));
	  creator.appendChild(document.createTextNode(" "));	   	    
	}
    ''')
    
    #div and table comment style
    request.writeln('''
	comment.style.border = "1px solid #3399FF";
        comment.style.padding = "5px";
        comment.style.margin = "0 0 10px";
	comment.id = itemid;
	
        table.border = 0;
        table.cellspacing = 0;
        table.cellpadding = 0;
        table.width = "100%";
    ''')

    # end of the processAdd function
    request.writeln('''
        }
    ''')

    # processRemove and processEdit functions
    request.writeln('''    
        function processDelete(itemid) {
          var body = document.getElementById('commentDiv');
          var item = document.getElementById(itemid);
          body.removeChild(item);
        }
        
        function processEdit(itemid, itemtext, creatorid) {
          // change the text
          var span = document.getElementById("text" + itemid);
          for (var i = 0; i < span.childNodes.length; i++) {
            if (span.childNodes[i].nodeType == 3) { // IE doesn't recognize the TEXT_NODE constant
              span.removeChild(span.childNodes[i]);
              span.appendChild(document.createTextNode(itemtext));
              break;
            } 
          }
        }
        
        function confirmDelete(itemid) {
          if (confirm('Delete this item?')) {
            sendEvent('delete_comment', itemid);
          }          
        }
       
        function showMessage(msg) {
          alert(msg);
        }
       
      </script>
    ''')       
    
  def send_input(self, request):
    '''Sends the input frame, where users can submit new comments'''
    rights = self.get_user_rights(request)
    request.writeln(
      HTML_HEAD + self.BODY_TAG_NO_CLOSE + ''' topmargin="8"><center>
    ''')
    
    if rights['Add']: # add right
      request.writeln(request.cgi_form(subview='send_input', reload='yes', gm_action="add_comment") + '''
        <div align="center"><textarea name="text" cols="50" rows="2" style="width:80%"></textarea></div>
        <div align="center"><input type="submit" value="Add" name="submit"></div>
        </form>
      ''')
      if request.getvalue('reload', '') == 'yes': # this comes from send_editform below
        request.writeln("<script language='JavaScript' type='text/javascript'>parent.refreshEvents();</script>")
      request.writeln('''
        </body>
        </html>
      ''')
    
    
  def send_editform(self, request):
    '''Sends the input frame for editing of an item'''
    item = datagate.get_item(request.getvalue('itemid', ''))
    request.writeln(
      HTML_HEAD + self.BODY_TAG_NO_CLOSE + ''' topmargin="8"><center>
    ''')
    request.writeln('''
      ''' + request.cgi_form(subview='send_input', reload='yes', gm_action="edit_comment", itemid=item.id) + '''
      <div align="center"><textarea name="text" cols="50" rows="2" style="width:80%">''' + item.text + '''</textarea></div>
      <div align="center"><input type="submit" name="submit" value="Save"> <input type="submit" name="submit" value="Cancel"></div>
      </form>
      </body>
      </html>
      ''')
    

  ###################################
  ###   Actions

  def get_initial_events(self, request, rootid):
    '''Retrieves a list of initial javascript calls that should be sent to the client
       when the view first loads.  Typically, this is a series of add_processor
       events.'''
    events = []
    root = datagate.get_item(rootid)
    comments = root.search1(name="comments")
    if comments:
      for item in comments.get_child_items():
        events.append(self._create_add_event(item))
    return events  
  
  def _create_add_event(self, item):
    log.info(str(item));
    subitems = []
    creator = datagate.get_item(item.creatorid)
    for si in item.get_child_items():
      siCreator = datagate.get_item(si.creatorid)
      subitems.append([si.text, siCreator.name, siCreator.email]);
    log.info(str(subitems))
    return Event('processAdd', item.id, item.text, item.time, creator.id, creator.name, creator.email, subitems)

  def add_comment_action(self, request):
    '''Responds to an add from the browser.'''
    # create the new item
    text = request.getvalue('text', '')
    creator = request.session.user
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    comments = root.search1(name="comments")
    item = datagate.create_item(creatorid=creator.id, parentid=comments.id)
    item.text = text
    item.time = time.time()
    log.info(str(item.time))
    item.save()
    return self._create_add_event(item)
    
  def add_sub_comment_action(self, request):
    '''Responds to an add sub idea from the browser.'''
    # create the new item
    text = request.getvalue('text', '')
    creator = request.session.user
    comment = datagate.get_item(request.getvalue('itemid'))

    item = datagate.create_item(creatorid=creator.id, parentid=comment.id)
    item.text = text
    item.time = time.time()
    log.info(str(item.time))
    item.save()
    return self._create_add_event(comment)

  def _create_edit_event(self, item):
    return Event('processEdit', item.id, item.text, item.creatorid)   

  def edit_comment_action(self, request):
    '''Responds to an edit event from the browser.'''
    if request.getvalue("submit", '') == "Save":
      # perform the action
      item = datagate.get_item(request.getvalue('itemid'))
      item.text = request.getvalue('text', '')
      item.save()
      
      # return an edit event
      return self._create_edit_event(item)   
    
  def delete_comment_action(self, request, itemid):
    '''Responds to a delete event from the browser'''
    datagate.del_item(itemid)
    return Event('processDelete', itemid)

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

  def savetitle_action(self, request):
    activity = datagate.get_item(request.getvalue('itemid', ''))
    activity.commentertitle = request.getvalue('title', '')
    activity.commenterdirection = request.getvalue('direction', 'newest')
    activity.save()
