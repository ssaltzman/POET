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
import Directory
import datagate
import BaseView
import TimedDict
import math
import time
import threading


class Rating(BaseView.BaseView):
  NAME = 'Rating'
  rights_list = [ 'View Tree', 'View Author', 'Add Sibling', 'Add Child', 'Edit', 'Delete', 'Comment Visibility', 'Rate Comments', 'Comment Rating Feedback', 'Number of Ratings', 'Overall Group Feedback', 'Overall User Feedback', 'Individual Pacing' ]
  
  def __init__(self):
    BaseView.BaseView.__init__(self)
    self.interactive = 1
    self.log_file_lock = threading.RLock()
    
    
    
  #########################################################
  ###   Main content for clients
  
  def send_content(self, request):
    subview = request.getvalue('_subview')
    if subview == 'content':
      self.send_initial_content(request)
    
    else:
      self.send_frames(request)  
    
    
  def send_frames(self, request):
    '''The frames'''
    activity = datagate.get_item(request.getvalue('global_rootid', ''))
    rights = self.get_user_rights(request)
    feedback_height = '0'
    feedback_view = 'Blank'
    if rights['Overall Group Feedback'] or rights['Overall User Feedback']:  # do we need the feedback window?
      feedback_height = '55'
      feedback_view = request.getvalue('view', 'Rating')
    
    request.writeln(HTML_HEAD + '''
      <frameset border='1' rows="''' + feedback_height + ''',*">
        <frame name='feedback' marginheight='0' marginwidth='0' src=\'''' + request.cgi_href(view='RatingDashboard') + '''\'>
        <frame name='content' marginheight='0' marginwidth='0'  src=\'''' + request.cgi_href(_subview='content') + '''\'>
      </frameset>
      </html>
    ''')
  

  def send_initial_content(self, request):
    '''Sends the threader content'''
    rights = self.get_user_rights(request)
    activity = datagate.get_item(request.getvalue('global_rootid', ''))
    title = request.getvalue('title', '')
    treeroot = activity.search1(name='treeroot')
    
    request.writeln(HTML_HEAD_NO_CLOSE + '''
      <script language='JavaScript' type='text/javascript'>
        function Item(id, creatorid, creatorname, creatoremail, parentid, previousid, text, visibility, ratings) {
          this.id = id;
          this.creatorid = creatorid;
          this.creatorname = creatorname;
          this.creatoremail = creatoremail;
          this.parentid = parentid;
          this.previousid = previousid;
          this.text = text;
          // split the visibility into an associative array
          this.visibility = new Array();
          for (var i = 0; i < visibility.length; i++) {
            var parts = visibility[i].split('=');
            this.visibility[parts[0]] = parts[1];
          }
          // split the data into an associative array
          this.ratings = new Array();
          for (var i = 0; i < ratings.length; i++) {
            var parts = ratings[i].split('=');
            this.ratings[parts[0]] = parts[1];
          }
        }

        // the images for the ten-point rating scale        
        var rating_images = [ 'stars-0-0.gif', 'stars-0-5.gif', 'stars-1-0.gif', 'stars-1-5.gif', 'stars-2-0.gif', 'stars-2-5.gif', 'stars-3-0.gif', 'stars-3-5.gif', 'stars-4-0.gif', 'stars-4-5.gif', 'stars-5-0.gif' ];
        
        // an in-memory tree holding the AddEvents that are used to populate the tree
        var root = new Item("''' + treeroot.id + '''", "", "", "", "", "", "ROOT", new Array(), new Array());
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
          var cellBorder = '1px solid #CCCCFF';
          var cellPadding = '0px 0px 0px 0px';
          var table = document.createElement("table");
          table.id = item.id;
          table.border = 0;
          table.cellSpacing = 0;
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
          td.style.padding = cellPadding;
          td.style.borderBottom = cellBorder;
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
          img.src = "''' + join(WEB_PROGRAM_URL, 'icon-plus.png') + '''";
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
      
    # hide comments
    if rights['View Tree'] and rights['Comment Visibility']:
      request.writeln('''
          // hide comment check box
          td = tr.appendChild(document.createElement("td"));
          td.style.padding = cellPadding;
          td.style.borderBottom = cellBorder;
          td.vAlign = "top";
          td.align = "center";
          td.width = 1;  // some width less than the actual width of the input box (browser will override to give minimal width)
          var checker = td.appendChild(document.createElement('input'));
          checker.value = 'visible';
          checker.name = 'visible';
          checker.type = 'checkbox';
          checker.itemid = item.id;
          checker.id = 'visibility' + item.id;
          checker.onchange = changeCommentVisibility;
          if (item.visibility["''' + request.session.user.id + '''"] == '1') {
            checker.checked = true;
          }
      ''')
      
    # the folder icon
    if rights['View Tree']:
      request.writeln('''
          // the folder image cell
          td = tr.appendChild(document.createElement("td"));
          td.style.padding = cellPadding;
          td.style.borderBottom = cellBorder;
          td.vAlign = "top";
          td.align = "right";
          td.width = 16 + (depth * 16) + 5; // +5 for a little padding, folder icons are 16 wide
          for (var i = 0; i < depth; i++) {
            img = td.appendChild(document.createElement("img"));
            img.src = "''' + join(WEB_PROGRAM_URL, 'spacer-10px.png') + '''";
            img.alt = "&nbsp;&nbsp;";
          }
          a = td.appendChild(document.createElement("a"));
          a.href = "javascript:selectItem('" + item.id + "');";
          img = a.appendChild(document.createElement("img"));
          img.border = 0;
          img.id = 'icon' + item.id;
      ''')
      if rights['Comment Visibility']:
        request.writeln('''
          img.src = "''' + join(WEB_PROGRAM_URL, 'letter_n.gif') + '''";
        ''')
      else:
        request.writeln('''
          img.src = "''' + join(WEB_PROGRAM_URL, 'notepad.png') + '''";
        ''')
      
    # the text span part
    if rights['View Tree']:
      request.writeln('''
          // the text span
          td = tr.appendChild(document.createElement("td"));
          td.style.padding = cellPadding;
          td.style.borderBottom = cellBorder;
          td.vAlign = "center";
          td.align = "left";
          a = td.appendChild(document.createElement("a"));
          a.id = "ahref" + item.id;
          a.href = "javascript:selectItem('" + item.id + "');";
          a.style.paddingTop = "2px";
          a.style.paddingBottom = "2px";
          a.style.paddingLeft = "4px";
          a.style.paddingRight = "4px";
          a.itemid = item.id;
          a.appendChild(document.createTextNode(item.text));
          updateColor(item);
      ''')
      
    # the second cell
    if rights['View Tree']:
      request.writeln('''
          // the right cell
          td = tr.appendChild(document.createElement("td"));
          td.style.padding = cellPadding;
          td.style.borderBottom = cellBorder;
          td.align = "right";
          td.vAlign = "center";
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
      
    # add the ratings
    request.writeln('''
          // ratings for this item
          td.appendChild(document.createTextNode(" "));
          span = td.appendChild(document.createElement("span"));
          span.id = "ratingSpan" + item.id;
          processRatings(item, span);
    ''')

    # select the first item
    request.writeln('''
          // if the item is the root item, select it automatically (just so something is selected)
          if (item == root.firstChild) {
            selectItem(item.id);
          }
        }
    ''')
      
    # ratings function
    rating_names = self.get_rating_names(activity)
    rights = self.get_user_rights(request)
    if rights['Rate Comments']:
      no_rating_rights = 'false'
    else:
      no_rating_rights = 'true'
    
    # short circuit
    if rating_names == None or len(rating_names) == 0:
      request.writeln('''
      function processRatings(item, span) {
      }
      ''')
    else:    
      # send the html  
      request.writeln('''
        function processRatings(item, span) {
          var select = null;
          var option = null;
          var img = null;
          var button = null;
  
          // clear it out          
          while (span.childNodes.length > 0) {
            span.removeChild(span.firstChild);
          }
  
          var userratings = new Array();
          var allRated = true;
          var ratingMaxes = new Array();
          var ratingAdjustments = new Array();
      ''')
      for name in rating_names:
        request.writeln('''
          ratingMaxes["''' + name + '''"] = ''' + str(self.get_rating_max_option_value(activity, name)) + ''';
          ratingAdjustments["''' + name + '''"] = ''' + str(self.get_rating_adjustment(activity, name)) + ''';
          if (''' + no_rating_rights + ''' || item.ratings["rating_''' + name + '_' + request.session.user.id + '''"] || item.creatorid == "''' + request.session.user.id + '''") { // I've already rated it or it's my comment
            for (var key in item.ratings) { 
              var parts = key.split("_"); // parts = [ "rating", name, userid ]
              if (parts[1] == "''' + name + '''") { // rating for this name from some user
                if (!userratings[parts[2]]) { // add an array item for this userid
                  userratings[parts[2]] = new Array();
                }
                userratings[parts[2]]["''' + name + '''"] = item.ratings[key];
              }
            }
            
          }else{ // I haven't rated this one yet
            allRated = false;
            select = document.createElement("select");
            select.id = "rating''' + name + '''" + item.id;
            span.appendChild(select); // can't add until id is set
            option = document.createElement("option");
            option.value = "''' + name + '''";
            option.text = "''' + name + ''':";
            select.options[select.options.length] = option; 
            option = document.createElement("option");
            option.value = "''' + name + '''";
            option.text = "";
            select.options[select.options.length] = option; 
        ''')
        for option in self.get_rating_options(activity, name):
          request.writeln('''
            option = document.createElement("option");
            option.value = "''' + str(option[0]) + '''";
            option.text = "''' + option[1] + '''";
            select.options[select.options.length] = option; 
          ''')
        request.writeln('''
          }
        ''')
      request.writeln('''
          if (allRated) { // I've rated this one in all areas, so show the result
      ''')
      if rights['Comment Rating Feedback']:
        request.writeln('''
            // calculate the rating value
            var scale = 10.0;
            var total = 0.0;
            var n = 0;
            for (var userid in userratings) {
              var userProduct = 1.0;
              var maxProduct = 1.0;
              for (var rating in userratings[userid]) {
                userProduct *= parseFloat(userratings[userid][rating]) * ratingAdjustments[rating];
                maxProduct *= ratingMaxes[rating];
              }
              total += (userProduct * (scale / maxProduct));
              n += 1;
            }
            if (n > 0) {
              var ratingValue = total / n;
              var ratingValueInt = Math.round(ratingValue);
              img = span.appendChild(document.createElement("img"));
              img.src = "''' + WEB_PROGRAM_URL + '''/" + rating_images[ratingValueInt];
            }
        ''')
      if rights['Number of Ratings']:
        request.writeln('''
            span.appendChild(document.createTextNode(" (" + n + ")"));
        ''')
      request.writeln(''' 
          }else if (!''' + no_rating_rights + ''') {
            span.appendChild(document.createTextNode("  "));
            button = span.appendChild(document.createElement("button"));
            button.appendChild(document.createTextNode("Rate"));
            button.onclick = saveRating;
            button.itemid = item.id;
          }
        }
      ''')
      
      kargs = { 'action':'saverating', 'itemid':None, 'frame':'events' }
      request.writeln('''
        function saveRating(evt) {
          evt = (evt) ? evt : ((event) ? event : null);
          var obj = (evt.target) ? evt.target : ((evt.srcElement) ? evt.srcElement : null);
          var id = obj.itemid;
          var url = "&itemid=" + id;
          // ensure all ratings are assigned
      ''')
      for name in rating_names:
        kargs['rating_' + name] = None
        request.writeln('''
          if (document.getElementById("rating''' + name + '''" + id)) { // we might not have shown it if it got rated already
            if (document.getElementById("rating''' + name + '''" + id).value == "''' + name + '''") {
              alert("Please give a rating for ''' + name + '''.");
              return;
            }
            url += "&rating_''' + name + '''=" + document.getElementById("rating''' + name + '''" + id).value;
          }
        ''')
      request.writeln('''
          url = "''' + request.cgi_href(**kargs) + '''" + url;
          getEvents().location.href = url;
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
        
        function processEdit(item) {
          var ahref= document.getElementById("ahref" + item.id);
          for (var i = 0; i < ahref.childNodes.length; i++) {
            if (ahref.childNodes[i].nodeType == 3) { // IE doesn't recognize the TEXT_NODE constant
              ahref.removeChild(ahref.childNodes[i]);
              ahref.appendChild(document.createTextNode(item.text));
              break;
            }
          }
          
          // update the rating
          var span = document.getElementById("ratingSpan" + item.id);
          processRatings(item, span, document);
        }
        
        function processVisibility(itemid, userid, visible) {
          var item = getItem(itemid);
          item.visibility[userid] = visible;          
          if (userid == "''' + request.session.user.id + '''") {
            item.visible = visible;
            var checker = document.getElementById('visibility' + itemid);
            checker.checked = (visible == 1);
            updateColor(item);
            var icon = document.getElementById("icon" + itemid);
    ''')  
    if rights['Comment Visibility']:
      request.writeln('''            
            if (icon.src != "''' + join(WEB_PROGRAM_URL, 'letter_r.gif') + '''") {
              icon.src = "''' + join(WEB_PROGRAM_URL, 'letter_r.gif') + '''";
            }
      ''')
    request.writeln('''
          }
        }
        
        function updateColor(item) {
          var ahref = document.getElementById("ahref" + item.id);
          if (ahref == selected) {
            ahref.style.color = "#FFFFFF";
            ahref.style.backgroundImage = "url(''' + join(WEB_PROGRAM_URL, 'background1.png)') + '''";
          }else{
            ahref.style.backgroundImage = "";
            if (item.visibility["''' + request.session.user.id + '''"] == '1') {
              ahref.style.color = "#000000";
            }else{
              ahref.style.color = "#666666";
            }
          }
          if (item.visibility["''' + request.session.user.id + '''"] == '1') {
            ahref.style.fontWeight = 'bold';
          }else{
            ahref.style.fontWeight = 'normal';
          }
        }
        
        var selected = null;
        function selectItem(id) {
          // unselect the previous one
          if (selected != null) {
            var item = getItem(selected.itemid);
            selected = null;
            updateColor(item);
          }
          // select the new one
          if (id) {
            var item = getItem(id);
            selected = document.getElementById("ahref" + id);
            updateColor(item);
    ''')
    if rights['Comment Visibility']:
      request.writeln('''   
            var icon = document.getElementById("icon" + id);
            if (icon.src != "''' + join(WEB_PROGRAM_URL, 'letter_r.gif') + '''") {
              icon.src = "''' + join(WEB_PROGRAM_URL, 'letter_r.gif') + '''";
            }
      ''')
    request.writeln('''
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
          var newtext = prompt("Edit Text:", text);
          // send the event via an events frame refresh
          if (newtext != null && newtext != '' && newtext != text) {
            newtext = encode(newtext);
            getEvents().location.href = "''' + request.cgi_href(frame='events', gm_action='edit_item', itemid=None, text=None) + '''&itemid=" + id + "&text=" + newtext;
            return;
          }
          getEvents().enableRefresh();
        }
        
        function changeCommentVisibility(evt) {
          var checker = getEventSource(evt);
          if (checker && checker.checked) {
            getEvents().location.href = "''' + request.cgi_href(frame='events', gm_action='change_item_visibility', itemid=None, visible=1) + '''&itemid=" + checker.itemid;
          }else if (checker) {
            getEvents().location.href = "''' + request.cgi_href(frame='events', gm_action='change_item_visibility', itemid=None, visible=0) + '''&itemid=" + checker.itemid;
          }
        }

      </script>
      </head>
      <body topmargin="4" id='outputBody' onLoad='getEvents().refreshEvents()'>
    ''')
    if title != '':
      request.writeln('<div align="center" style="padding: 5px; font-weight: bold">' + title + '</div>')      
    request.writeln('''
      </body>
      </html>
    ''')    
    
    
  ###################################
  ###   Actions

  def _create_event(self, item, func):
    '''Private method to create an add event'''
    creator = datagate.get_item(item.creatorid)
    visibility = []
    for key, val in item.__dict__.items():
      if key.find('visibility_') == 0:
        visibility.append('"' + key[len('visibility_'):] + '=' + val + '"')
    ratings = []
    for key, val in item.__dict__.items():
      if key.find('rating_') == 0:
        ratings.append('"' + key + '=' + val + '"')
    return 'content.' + func + '(new parent.content.content.Item("%s", "%s", decode("%s"), decode("%s"), "%s", "%s", decode("%s"), %s, %s))' % \
      ( item.id, 
        creator.id, 
        encode(creator.name),
        encode(creator.email),
        item.parentid,
        item.get_previousid(),
        encode(item.text),
        'new Array(' + ','.join(visibility) + ')',
        'new Array(' + ','.join(ratings) + ')',
      )
    

  def get_initial_events(self, request, rootid):
    '''Retrieves a list of initial javascript calls that should be sent to the client
       when the view first loads.  Typically, this is a series of add_processor
       events.'''
    root = datagate.get_item(rootid)
    treeroot = root.search1(name="treeroot")
    return [ self._create_event(item, 'processAdd') for item in treeroot.get_child_items(deep=1) ]
    

  def add_item_action(self, request):
    # perform the action
    rights = self.get_user_rights(request)
    creator = request.session.user
    item = datagate.create_item(creatorid=creator.id, parentid=request.getvalue('parentid'), previousid=request.getvalue('previousid'))
    item.text = request.getvalue('text', '')
    item.save()
    
    # send the event to the client
    return [ self._create_event(item, 'processAdd') ]
    
  
  def remove_item_action(self, request):
    datagate.del_item(request.getvalue('itemid', ''))
    return [ 'content.processRemove("' + request.getvalue('itemid', '') + '")' ]
  
  
  def edit_item_action(self, request):
    # perform the action
    item = datagate.get_item(request.getvalue('itemid', ''))
    item.text = request.getvalue('text', '')
    item.save()
    
    # send the even to the client
    return [ self._create_event(item, 'processEdit') ]
    
    
  def saverating_action(self, request):
    '''Saves a rating for the current user'''
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    rating_names = self.get_rating_names(root)
    item = datagate.get_item(request.getvalue('itemid'))
    for name in rating_names:
      setattr(item, 'rating_' + name + '_' + request.session.user.id, request.getvalue('rating_' + name))
    item.save()
    
    # send the event back to the client
    return [ self._create_event(item, 'processEdit') ]
    
    
  def change_item_visibility_action(self, request):
    '''Changes a comment's visibility'''
    item = datagate.get_item(request.getvalue('itemid', ''))
    if request.getvalue('visible', '') == '1':
      visible = '1'
    else:
      visible = '0'
    setattr(item, 'visibility_' + request.session.user.id, visible)
    item.save()
    return [ 'content.processVisibility("' + item.id + '", "' + request.session.user.id + '", ' + visible + ')' ]
    
    
  #########################################################
  ###   Administrator methods
  
  def initialize_activity(self, request, new_activity):
    '''Called from the Administrator.  Sets up the activity'''
    treeroot = datagate.create_item(creatorid=request.session.user.id, parentid=new_activity.id)
    treeroot.name = 'treeroot'
    treeroot.save()
    
    # set up the first item in the tree
    initialnode = datagate.create_item(creatorid=request.session.user.id, parentid=treeroot.id)
    initialnode.text = 'Root Item'
    initialnode.save()
      
    # set the rating information
    new_activity.ratingMultiplier = '1'
    new_activity.commentMultiplier = '1'
    new_activity.ratingsScoreMultiplier = '1'
    new_activity.ratingRefreshRate = '20'
    new_activity.ratingGoal = '100'
    new_activity.pacingDuration = '180'
    new_activity.pacingValues = '30 Fast\n15 Medium\n0 Slow'
    new_activity.pacingLogFile = ''
    new_activity.estimatedMeetingDuration = '0'
    new_activity.save()

    # set user rights
    BaseView.BaseView.initialize_activity(self, request, new_activity)



  
  def send_admin_page(self, request):
    '''Sends an administrator page for this view.'''
    activity = datagate.get_item(request.getvalue('itemid', ''))
    
    # the group rights
    request.writeln('<hr>')
    request.writeln('<p>&nbsp;</p>')
    BaseView.BaseView.send_admin_page(self, request)    
    
    # point values
    request.writeln('<hr>')
    request.writeln('<p>&nbsp;</p>')
    request.writeln('<div>')
    request.writeln(request.cgi_form(gm_action='Rating.formula', ratingMultiplier=None, commentMultiplier=None, ratingsScoreMultiplier=None, ratingRefreshRate=None))
    request.writeln('<b>Overall Individual Rating</b> = ')
    request.writeln('<tt>')
    request.writeln('<input type="text" name="ratingMultiplier" value="' + activity.ratingMultiplier + '" size="5"> x NumRatings')
    request.writeln('&nbsp;+&nbsp;')
    request.writeln('<input type="text" name="commentMultiplier" value="' + activity.commentMultiplier + '" size="5"> x NumComments')
    request.writeln('&nbsp;+&nbsp;')
    request.writeln('<input type="text" name="ratingsScoreMultiplier" value="' + activity.ratingsScoreMultiplier + '" size="5"> x RatingsScore')
    request.writeln('<p></tt>')
    request.writeln('Refresh every <input type="text" name="ratingRefreshRate" value="' + activity.ratingRefreshRate + '" size="5"> seconds')
    request.writeln('<p>')
    request.writeln('<input type="submit" value="Save">')
    request.writeln('</form>')
    request.writeln('<p>')
    request.writeln('(Overall group rating is the average of the overall individual ratings)')
    request.writeln('</div>') 
    
    # pacing messages
    request.writeln('<hr>')
    request.writeln('<p>&nbsp;</p>')
    request.writeln('<div>')
    request.writeln(request.cgi_form(gm_action='Rating.pacing', pacingValues=None, pacingDuration=None, pacingLogFile=None))
    request.writeln('<b>Pacing:</b><p>')
    request.writeln('Time Interval For Measurement: <input type="text" size="10" name="pacingDuration" value="' + activity.pacingDuration + '"> seconds')
    request.writeln('<p>')
    request.writeln('Specify the incremental values and messages (separated by a space) that scores should change each interval:<br>')
    request.writeln('<textarea name="pacingValues" rows="5" cols="30">' + activity.pacingValues + '</textarea>')
    request.writeln('<p>')
    request.writeln('Log File (absolute path): <input type="text" name="pacingLogFile" size="40" value="' + activity.pacingLogFile + '">')
    request.writeln('<p>')
    request.writeln('<input type="submit" value="Save">')
    request.writeln('</form>')
    request.writeln('</div>')
    
    # the rating scales
    request.writeln('<hr>')
    request.writeln('<p>&nbsp;</p>')
    request.writeln('<div>')
    request.writeln(request.cgi_form(gm_action='Rating.newrating', name=None, adjustment=None, options=None))
    request.writeln('<b>Ratings:</b>')
    request.writeln('<br>')
    request.writeln('Each comment can be rated on multiple scales.  The RatingsScore (in the overall formula above) is the sum of (rating option value * adjustment) for each of the ratings defined below.')
    request.writeln('Each line of the rating options below is entered as the value for the option, followed by a space, followed by the text to place in the select drop down.')
    request.writeln('<table border=1 cellspacing=0 cellpadding=2>')
    request.writeln('<tr>')
    request.writeln('<th>Name</th>')
    request.writeln('<th>Adjustment</th>')
    request.writeln('<th>Options</th>')
    request.writeln('<th>Actions</th>')
    request.writeln('</tr>')
    for name in self.get_rating_names(activity):
      request.writeln('<tr>')
      request.writeln('<td valign="top">' + getattr(activity, 'rating_' + name) + '</td>')
      request.writeln('<td valign="top">' + getattr(activity, 'ratinginfo_' + name + '_adjustment') + '</td>')
      request.writeln('<td valign="top"><pre>' + getattr(activity, 'ratinginfo_' + name + '_options') + '</pre></td>')
      request.writeln('''<td valign="top" align="center"><a href="javascript:confirm_url('Delete this rating?', \'''' + request.cgi_href(name=name, gm_action='Rating.delrating', options=None, adjustment=None) + '''\');">Delete</a></td>''')
      request.writeln('</tr>')
    request.writeln('<tr>')
    request.writeln('<td valign="top" align="center"><input type="text" name="name" value="Please Rate" size="20" onfocus="clearField(this);"></td>')
    request.writeln('<td valign="top" align="center"><input type="text" name="adjustment" value="1" size="5"></td>')
    request.writeln('<td valign="top" align="center"><textarea rows=6 cols=20 name="options">5 5 - Excellent\n4 4\n3 3 - Fair\n2 2\n1 1 - Poor</textarea></td>')
    request.writeln('<td valign="top" align="center"><input type="submit" value="Add" name="submit"></td>')
    request.writeln('</tr>')
    request.writeln('</table>')
    request.writeln('</form>')
    request.writeln('</div>')
    request.writeln('</center>')
    
    
  def get_rating_names(self, activity):
    '''Returns a list of rating names that exist for this view'''
    names = []
    for key in activity.__dict__.keys():
      if len(key) > 8 and key[0:7] == 'rating_':
        names.append(key[7:])
    return names
    
  
  def get_rating_options(self, activity, name):
    '''Returns the rating options for a given rating name as a list of tuples: (value, text)'''
    options = []
    for line in getattr(activity, 'ratinginfo_' + name + '_options').strip().split('\n'):
      line = line.strip()
      pos = line.find(' ')
      if pos > 0:
        options.append((int(line[0:pos]), line[pos+1:]))
    return options
    
    
  def get_rating_max_option_value(self, activity, name):
    '''Returns the maximum rating value for the given rating name in the given activity'''
    options = self.get_rating_options(activity, name)
    if len(options) == 0:
      return 0
    val = options[0][0]
    for option in options:
      val = max(val, option[0])
    return val
    
    
  def get_rating_adjustment(self, activity, name):
    '''Returns the adjustment value for the given rating name in the given activity as an int'''
    return int(getattr(activity, 'ratinginfo_' + name + '_adjustment'))
    
  
  def newrating_action(self, request):
    activity = datagate.get_item(request.getvalue('itemid', ''))
    name = request.getvalue('name', '')
    setattr(activity, 'rating_' + name, name)
    setattr(activity, 'ratinginfo_' + name + '_adjustment', request.getvalue('adjustment', ''))
    setattr(activity, 'ratinginfo_' + name + '_options', request.getvalue('options', ''))
    activity.save()

  
  def delrating_action(self, request):
    activity = datagate.get_item(request.getvalue('itemid', ''))
    name = request.getvalue('name', '')
    delattr(activity, 'rating_' + name)
    delattr(activity, 'ratinginfo_' + name + '_adjustment')
    delattr(activity, 'ratinginfo_' + name + '_options')
    activity.save()


  def formula_action(self, request):
    activity = datagate.get_item(request.getvalue('itemid', ''))
    activity.ratingMultiplier = request.getvalue('ratingMultiplier', '0')
    activity.commentMultiplier = request.getvalue('commentMultiplier', '0')
    activity.ratingsScoreMultiplier = request.getvalue('ratingsScoreMultiplier', '0')
    activity.ratingRefreshRate = request.getvalue('ratingRefreshRate', '20')
    activity.save()


  def pacing_action(self, request):  
    activity = datagate.get_item(request.getvalue('itemid', ''))
    activity.pacingDuration = request.getvalue('pacingDuration', activity.pacingDuration)
    activity.pacingValues = request.getvalue('pacingValues', activity.pacingValues)
    activity.pacingLogFile = request.getvalue('pacingLogFile', '')
    activity.save()