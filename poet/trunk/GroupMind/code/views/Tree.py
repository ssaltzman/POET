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


class Tree(BaseView.BaseView):
  NAME = 'Tree'
  rights_list = [ 'View Tree', 'View Author', 'Add Sibling', 'Add Child', 'Edit', 'Delete' ]
  icon = 'folder.png'
  initial_text = 'Tree Root'

  def __init__(self):
    BaseView.BaseView.__init__(self)
    self.interactive = 1
    
     
  def initialize_activity(self, request, root, tree_links=None):
    '''Called from the administrator.  Initializes the tree given a tree root item and tree links item'''
    treeroot = datagate.create_item(creatorid=request.session.user.id, parentid=root.id)
    treeroot.name = 'treeroot'
    treeroot.save()
    
    # set up the first item in the tree
    initialnode = datagate.create_item(creatorid=request.session.user.id, parentid=treeroot.id)
    initialnode.text = self.initial_text
    initialnode.save()
    if tree_links != None:
      self.initialize_item(request, initialnode, tree_links.id)
      
    # set user rights
    BaseView.BaseView.initialize_activity(self, request, root)


  def send_content(self, request):
    '''Sends the content pane to the browser'''
    # the tree needs the following parameters to set up its links:
    linkview = request.getvalue("linkview", "")    # the view parameter for the link
    linkframe = request.getvalue("linkframe", "")  # the frame to go to (blank for top-level)
    treelinkid = request.getvalue("treelinkid", "")
    rights = self.get_user_rights(request)
    activity = datagate.get_item(request.getvalue('global_rootid', ''))
    title = request.getvalue('title', '')
    treeroot = activity.search1(name='treeroot')
    
    request.writeln(HTML_HEAD_NO_CLOSE + '''
      <script language='JavaScript' type='text/javascript'>
        function Item(id, creatorid, creatorname, creatoremail, parentid, previousid, text, linkid) {
          this.id = id;
          this.creatorid = creatorid;
          this.creatorname = creatorname;
          this.creatoremail = creatoremail;
          this.parentid = parentid;
          this.previousid = previousid;
          this.text = text;
          this.linkid = linkid;
        }
        
        // an in-memory tree holding the AddEvents that are used to populate the tree
        var root = new Item("''' + treeroot.id + '''", "", "", "", "", "ROOT");
        root.rootid = "''' + treeroot.id + '''";
        root.firstChild = null;
        root.nextSibling = null;
        root.previousSibling = null;
        
        function getBody() { // convenience method
          return document.getElementById('outputBody');
        }
        
        function getItemRecurse(node, id, depth) { // returns both item and depth
          if (node.id == id) { // am I the right one?
            return new Array(node, depth);
          }
          var child = node.firstChild;
          while (child != null) {
            var found = getItemRecurse(child, id, depth + 1); 
            if (found != null) {
              return found;
            }
            child = child.nextSibling;
          }
          return null;
        }

        function getItem(id) {
          if (id != null) {
            var item = getItemRecurse(root, id, -1);
            if (item != null) {
              return item[0];
            }
          }
          return null;
        }

        function getDepth(id) {
          if (id != null) {
            var item = getItemRecurse(root, id, -1);
            if (item != null) {
              return item[1];
            }
          }
          return 0;
        }
        
        function processAdd(item) {
    ''')
    
    controlCellWidth = 5;  # start with a little padding
    if rights['Add Sibling']: controlCellWidth += 20  # each icon is 10 pixels wide
    if rights['Add Child']:   controlCellWidth += 10  # each icon is 10 pixels wide
    if rights['Edit']:        controlCellWidth += 10 + 3  # each icon is 10 pixels wide, +3 for spacer
    if rights['Delete']:      controlCellWidth += 10 + 3 # each icon is 10 pixels wide, +3 for spacer
    
    if rights['View Tree']:
      request.writeln('''
 
          // for my children, if I get any
          item.firstChild = null;
          item.nextSibling = null;
          item.previousSibling = null;

          // get my parent item
          var parent = root;
          if (item.parentid != null && item.parentid != '') {
            parent = getItem(item.parentid);
          }        
          item.parent = parent; // for a backwards link up the tree

          // get the previous item, if there is one, and add to the list
          var previous = getItem(item.previousid);
          if (previous == null) { // I need to go first
            var first = parent.firstChild;
            if (first == null) { // I'm the only one, so just add
              parent.firstChild = item;
            }else{
              first.previousSibling = item;
              item.nextSibling = first;
              parent.firstChild = item;
            }
          }else { // add after the previous
            item.previousSibling = previous;
            item.nextSibling = previous.nextSibling;
            previous.nextSibling = item;
            if (item.nextSibling != null) {
              item.nextSibling.previousSibling = item;
            }
          }

          // create the table and add to the body
          // I create the table tag manually so I can append it to whatever area I want
          var table = document.createElement("table");
          table.id = item.id;
          table.border = 0;
          table.cellSpacing = 2;
          table.cellPadding = 0;
          table.width = "100%";
          item.table = table; // link the table to the event

          // append it to the DOM at the right location
          var temp = item;
          while (temp != root && temp.nextSibling == null) {
            temp = temp.parent;
          }

          if (temp != root) {
            getBody().insertBefore(table, temp.nextSibling.table);
          }else{
            getBody().appendChild(table);  // if all else fails, just add to the end
          }

          // set the table html
          var depth = getDepth(item.id);
          var tbody = table.appendChild(document.createElement("tbody"));
          var tr = tbody.appendChild(document.createElement("tr"));
          var td = null;
          var img = null;
          var a = null;
          var select = null;
          var option = null;
          var button = null;
          var span = null;
          
          // the controls cell
          td = tr.appendChild(document.createElement("td"));
          td.vAlign = "top";
          td.align = "center";
          td.width = ''' + str(controlCellWidth) + ''';
      ''')  


    # add sibling    
    if rights['View Tree'] and rights['Add Sibling']:
      request.writeln('''  
          // insert after
          a = td.appendChild(document.createElement("a"));
          a.href = "javascript:add('Add Item After:', '" + item.parentid + "','" + item.id + "');";
          img = a.appendChild(document.createElement("img"));
          img.border = "0";
          img.src = "''' + join(WEB_PROGRAM_URL, 'icon-down.png') + '''";
          
          // insert before
          if (item != root.firstChild) {
            a = td.appendChild(document.createElement("a"));
            a.id = "before" + item.id;
            a.href = "javascript:add('Add Item Before:', '" + item.parentid + "','" + item.previousid + "');";
            img = a.appendChild(document.createElement("img"));
            img.border = "0";
            img.src = "''' + join(WEB_PROGRAM_URL, 'icon-up.png') + '''";
          }else{
            img = td.appendChild(document.createElement("img"));
            img.border = "0";
            img.src = "''' + join(WEB_PROGRAM_URL, 'spacer-10px.png') + '''";
          }
          
          // we have to change the next item's "insert before" link
          if (item.nextSibling != null) {
            var link = document.getElementById('before' + item.nextSibling.id);
            if (link != null) {
              link.href = "javascript:add('Add Item Before:', '" + item.parentid + "','" + item.id + "')";
            }
          }
      ''')
      
    # add child  
    if rights['View Tree'] and rights['Add Child']:
      request.writeln('''          
          // insert below (one level down)
          a = td.appendChild(document.createElement("a"));
          a.href = "javascript:add('Add Child Item:', '" + item.id + "','last');";
          img = a.appendChild(document.createElement("img"));
          img.border = "0";
          img.src = "''' + join(WEB_PROGRAM_URL, 'icon-right.png') + '''";
      ''')
      
    # edit node
    if rights['View Tree'] and rights['Edit']:
      request.writeln('''
          // edit item
          img = a.appendChild(document.createElement("img"));
          img.border = "0";
          img.src = "''' + join(WEB_PROGRAM_URL, 'spacer-3px.png') + '''";
          a = td.appendChild(document.createElement("a"));
          a.href = "javascript:edit('" + item.id + "');";
          img = a.appendChild(document.createElement("img"));
          img.border = "0";
          img.src = "''' + join(WEB_PROGRAM_URL, 'icon-edit.png') + '''";
      ''')
      
    # delete node
    if rights['View Tree'] and rights['Delete']:
      request.writeln('''
          // delete item
          img = a.appendChild(document.createElement("img"));
          img.border = "0";
          img.src = "''' + join(WEB_PROGRAM_URL, 'spacer-3px.png') + '''";
          if (item != root.firstChild) {
            a = td.appendChild(document.createElement("a"));
            a.href = "javascript:parent.confirm_target_url('Delete this item and all subfolders?  \\n\\n(This cannot be undone!)\\', getEvents(), \'''' + request.cgi_href(frame='events', gm_action='remove_item', itemid=None) + '''&itemid=" + item.id + "');";
            img = a.appendChild(document.createElement("img"));
            img.border = "0";
            img.src = "''' + join(WEB_PROGRAM_URL, 'icon-delete.png') + '''";
          }else{
            img = td.appendChild(document.createElement("img"));
            img.border = "0";
            img.src = "''' + join(WEB_PROGRAM_URL, 'spacer-10px.png') + '''";
          }
      ''')
      
    # the folder icon
    if rights['View Tree']:
      request.writeln('''
          // the folder image cell
          td = tr.appendChild(document.createElement("td"));
          td.vAlign = "top";
          td.align = "right";
          td.width = 16 + (depth * 16) + 5; // +5 for a little padding, folder icons are 16 wide
          for (var i = 0; i < depth; i++) {
            img = td.appendChild(document.createElement("img"));
            img.src = "''' + join(WEB_PROGRAM_URL, 'spacer-10px.png') + '''";
            img.alt = "&nbsp;&nbsp;";
          }
          img = td.appendChild(document.createElement("img"));
          img.src = "''' + join(WEB_PROGRAM_URL, self.icon) + '''";
      ''')
      
    # the text span part
    if rights['View Tree']:
      request.writeln('''
          // the text span
          td = tr.appendChild(document.createElement("td"));
          td.vAlign = "top";
          td.align = "left";
          a = td.appendChild(document.createElement("a"));
          a.id = "ahref" + item.id;
          a.href = "javascript:selectItem('" + item.id + "');";
          a.style.paddingTop = "2px";
          a.style.paddingBottom = "2px";
          a.style.paddingLeft = "4px";
          a.style.paddingRight = "4px";
          a.style.color = "''' + COLOR_VERY_DARK + '''";
          a.appendChild(document.createTextNode(item.text));
      ''')
      
    # the second cell
    if rights['View Tree']:
      request.writeln('''
          // the right cell
          td = tr.appendChild(document.createElement("td"));
          td.align = "right";
          td.vAlign = "top";
          td.noWrap = true;
      ''')
      
    # node author
    if rights['View Tree'] and rights['View Author']:
      request.writeln('''    
          // the username/email link
          a = td.appendChild(document.createElement("a"));
          a.href = "mailto:" + item.creatoremail;
          a.appendChild(document.createTextNode(item.creatorname));
          td.appendChild(document.createTextNode(" "));
      ''')
      
    # select the first item
    request.writeln('''
          // if the item is the root item, select it automatically (just so something is selected)
          if (item == root.firstChild) {
            selectItem(item.id);
          }
        }
    ''')
      
    # the following shows on all screens
    request.writeln('''
        function processRemove(itemid) {
          var node = getItem(itemid);
          var body = getBody();

          // if the node is select, select the previous, parent, or root one
          if (selected == document.getElementById("ahref" + itemid)) {
            if (node.previousSibling != null) {
              selectItem(node.previousSibling.id);
            }else if (node.nextSibling != null) {
              selectItem(node.nextSibling.id);
            }else{
              selectItem(node.parent.id);
            }
          }

          // remove the node from the in-memory tree
          var previousSibling = node.previousSibling;
          var nextSibling = node.nextSibling;
          if (previousSibling == null) { // I'm the first child, so change the parent
            node.parent.firstChild = nextSibling;
          }else{
            previousSibling.nextSibling = nextSibling;
          }
          if (nextSibling != null) {
            nextSibling.previousSibling = previousSibling;
          }

          // determine the next element (we remove to this element)
          var next = null;
          if (node.nextSibling != null) { // if I have a next sibling, we remove to that
            next = node.nextSibling;
          }else {
            var temp = node.parent;
            while (temp != root && temp.nextSibling == null) {
              temp = temp.parent;
            }
            if (temp != root) {
              next = temp.nextSibling;
            }
          }

          // remove to the next table element
          var table = node.table;
          while ((next == null && table != null) || (next != null && table != next.table)) {
            var nexttable = table.nextSibling;
            body.removeChild(table);
            table = nexttable;
          }
        }
        
        function processEdit(itemid, itemtext) {
          var ahref= document.getElementById("ahref" + itemid);
          for (var i = 0; i < ahref.childNodes.length; i++) {
            if (ahref.childNodes[i].nodeType == 3) { // IE doesn't recognize the TEXT_NODE constant
              ahref.removeChild(ahref.childNodes[i]);
              ahref.appendChild(document.createTextNode(itemtext));
              break;
            }
          }
          
          // update the rating
          //var span = document.getElementById("ratingSpan" + itemid);
          //if (span) {
          //  processRatings(item, span, document);
          //}
        }
        
        var selected = null;
        function selectItem(id) {
          // unselect the previous one
          if (selected != null) {
            selected.style.color = "''' + COLOR_VERY_DARK + '''";
            selected.style.backgroundImage = "";
          }
          // select the new one
          var item = getItem(id);
          selected = document.getElementById("ahref" + id);
          selected.style.color = "#FFFFFF";
          selected.style.backgroundImage = "url(''' + join(WEB_PROGRAM_URL, 'background1.png)') + '''";
          if (parent.parent && parent.parent.''' + str(request.getvalue('target')) + ''') {
            parent.parent.''' + str(request.getvalue('target')) + '''.location.href = "''' + request.cgi_href(title=None, view=linkview, frame=linkframe, global_rootid=None) + '''&global_rootid=" + item.linkid + "&title=" + encode(item.text);
          }
        }

    ''')
    
    # functions to send normal add and edit events to the server
    request.writeln('''        

        /////////////////////////////////////////////////////
        ///  Functions to support client-side adding & editing
        ///  This initiates an add or edit event
        
        function add(title, parentid, previousid) {
          getEvents().disableRefresh();
          var text = prompt(title, '');
          if (text != null && text != '') {
            text = encode(text);
            getEvents().location.href = "''' + request.cgi_href(frame='events', gm_action='add_item', text=None, previousid=None, parentid=None) + '''&parentid=" + parentid + "&previousid=" + previousid + "&text=" + text;
            return;
          }
          getEvents().enableRefresh();
        } 
        
        function edit(id) {
          getEvents().disableRefresh();
          var ahref= document.getElementById("ahref" + id);
          var text = "";
          for (var i = 0; i < ahref.childNodes.length; i++) {
            if (ahref.childNodes[i].nodeType == 3) { // IE doesn't recognize the TEXT_NODE constant
              text = ahref.childNodes[i].nodeValue;
              break;
            }
          }
          // prompt the user for the new text
          var newtext = prompt("Edit Tree Item:", text);
          // send the event via an events frame refresh
          if (newtext != null && newtext != '' && newtext != text) {
            newtext = encode(newtext);
            getEvents().location.href = "''' + request.cgi_href(frame='events', gm_action='edit_item', itemid=None, text=None) + '''&itemid=" + id + "&text=" + newtext;
            return;
          }
          getEvents().enableRefresh();
        }
        
      </script>
      </head>
      ''' + HTML_BODY_NO_CLOSE + ''' topmargin="4" id='outputBody' onLoad='refreshEvents()'>
    ''')
    if title != '':
      request.writeln('<div align="center" style="padding: 5px; font-weight: bold">' + title + '</div>')      
    request.writeln('''
      </body>
      </html>
    ''')


    
  ###################################
  ###   Actions

  def _create_add_event(self, item):
    '''Private method to create an add event'''
    creator = datagate.get_item(item.creatorid)
    linkid = '';
    if hasattr(item, 'linkid'):
      linkid = item.linkid
    return 'processAdd(new parent.content.Item("%s", "%s", decode("%s"), decode("%s"), "%s", "%s", decode("%s"), "%s"))' % \
      ( item.id, 
        creator.id, 
        encode(creator.name),
        encode(creator.email),
        item.parentid,
        item.get_previousid(),
        encode(item.text),
        linkid,
      )
    

  def get_initial_events(self, request, rootid):
    '''Retrieves a list of initial javascript calls that should be sent to the client
       when the view first loads.  Typically, this is a series of add_processor
       events.'''
    root = datagate.get_item(rootid)
    treeroot = root.search1(name="treeroot")
    return [ self._create_add_event(item) for item in treeroot.get_child_items(deep=1) ]
    

  def add_item_action(self, request):
    # perform the action
    creator = request.session.user
    item = datagate.create_item(creatorid=creator.id, parentid=request.getvalue('parentid'), previousid=request.getvalue('previousid'))
    item.text = request.getvalue('text', '')
    item.save()
    
    # if this tree is in an analyzer, add the tree links id
    tree_links_id = request.getvalue('treelinkid', '')
    if tree_links_id: 
      linknode = datagate.create_item(creatorid=creator.id, parentid=tree_links_id)
      linknode.treenodeid = item.id
      item.linkid = linknode.id
      item.save()
      linknode.save()
      
    # send the event to the client
    return [ self._create_add_event(item) ]
    
  
  def remove_item_action(self, request):
    datagate.del_item(request.getvalue('itemid', ''))
    return [ 'processRemove("' + request.getvalue('itemid', '') + '")' ]
  
  def edit_item_action(self, request):
    # perform the action
    item = datagate.get_item(request.getvalue('itemid', ''))
    item.text = request.getvalue('text', '')
    item.save()
    
    # send the even to the client
    return [ 'processEdit("' + item.id + '",decode("' + encode(item.text) + '"))' ]
    
  

    
