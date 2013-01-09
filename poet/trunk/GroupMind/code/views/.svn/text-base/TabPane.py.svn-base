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
import Directory
import Events
import threading
import datagate
import os.path

class TabPane(BaseView.BaseView):
  NAME = 'Tab Pane'
  title = "Tabs"

  def __init__(self):
      BaseView.BaseView.__init__(self)
      self.lock = threading.Lock()
     
  #####################################
  ###   Client view methods
     
  def send_content(self, request):
    '''Shows a tab for each child'''
    action = request.getvalue('tpaction', '')
    if action == 'tabs':
      self.send_tabs(request)
      
    else:
      self.send_frames(request)
      

  def send_frames(self, request):
    request.writeln(HTML_HEAD)
    if request.getvalue('title', '') == '':
      request.writeln("<frameset border='0' rows='40, *'>")
    else:
      request.writeln("<frameset border='0' rows='60, *'>")
    request.writeln("<frame noresize marginheight='0' marginwidth='0' name='tabs' src='" + request.cgi_href(tpaction='tabs') + "'>")
    request.writeln("<frame noresize marginheight='0' marginwidth='0' name='tabdetail' src='" + request.cgi_href(global_view='Blank') + "'>")
    request.writeln("</frameset>")
    request.writeln("</html>")    
  
  
  def send_tabs(self, request):
    global_meetingid = request.getvalue('global_meetingid', '')
    # the calling view can send in a tabdefsid which is the parent of the tab definitions
    # if it isn't sent, we assume the root id is also the tab definitions, which means the tabdef and the tab data parent are the same
    tabdefs = datagate.get_child_items(request.getvalue('tabdefsid', request.getvalue('global_rootid', '')))

    # get the tabs from the database
    # the root id is the parent of where we'll store the values for each tab
    rootid = request.getvalue('global_rootid', '')
    tabs = datagate.get_child_items(rootid)
    tabsdict = {} # a dict relating the linkitemids to the tab objects
    for tab in tabs:
      tabsdict[tab.linkitemid] = tab

    # initial tab id and view    
    initialtabid = request.session.get_attribute('tabpaneid', '')
    initialtabview = 'Commenter' # default to something

    # ensure we have items for each tabdef
    for tabdef in tabdefs:
      # grab the view if this is our meeting
      if initialtabid == tabdef.id:
        initialtabview = tabdef.view
        
      # if not created yet on this node, create it
      if tabsdict.has_key(tabdef.id):
        tab = tabsdict[tabdef.id]
      else:
        # create the new tab
        tab = datagate.create_item(creatorid=request.session.user.id, parentid=rootid)
        tab.linkitemid = tabdef.id
        tab.save()
        
        # allow the view to initialize the new item
        BaseView.views[tabdef.view.lower()].initialize_activity(request, tab)
        
        # save in the tabsdict
        tabsdict[tab.linkitemid] = tab

      # ensure the rights haven't changed
      rights_changed = 0
      for key in tabdef.__dict__.keys():
        if len(key) > 12 and key[:12] == 'grouprights_':
          if getattr(tab, key) != getattr(tabdef, key):
            setattr(tab, key, getattr(tabdef, key))
            rights_changed = 1
      if rights_changed:
        tab.save()
    
    # ensure we have an initial tab to select
    if (initialtabid == '' or not tabsdict.has_key(initialtabid)) and len(tabdefs) > 0: 
      initialtabid = tabdefs[0].id
      initialtabview = tabdefs[0].view

    # the javascript for selection    
    request.writeln(HTML_HEAD_NO_CLOSE + '''
      <script language='JavaScript' type='text/javascript'>
      <!--
        var selected = null;
        function select(linkitemid, tabid, tabview) {
          // unselect the previous one
          if (selected != null) {
            selected.style.fontWeight = "Normal";
          }
          // select the new one
          selected = document.getElementById(tabid);
          selected.style.fontWeight = "Bold";
          parent.tabdetail.location.href="''' + request.cgi_href(view=None, global_rootid=None) + '''&global_rootid=" + tabid + "&sessionattribute=tabpaneid," + linkitemid + "&view=" + tabview;
        }      
        
        function initialLoad() {
          select("''' + initialtabid + '''", "''' + tabsdict[initialtabid].id + '''", "''' + initialtabview + '''");
        }
      //-->
      </script>
            
      <style type="text/css">
        .tab        
        {
          font-family: Helvetica;
          font-size: small;
          letter-spacing: 1px;
          word-spacing: 2px;
          padding-bottom: 5px;
          cursor: pointer; 
        }
      </style>      
    ''')
    request.writeln('</head>' + HTML_BODY_NO_CLOSE + ' style="padding: 5px" onLoad="javascript:initialLoad()">')

    # send the title, if there is one
    title = request.getvalue('title', '')
    if title != '':
      request.writeln('<div align="center" style="font-size: large; padding-bottom: 5px">' + title + '</div>')

    # send the tabs
    lasttab = len(tabdefs) - 1
    request.writeln('<table border="0" cellspacing="0" cellpadding="0" width="100%">')

    # header row
    request.writeln('<tr>')
    request.writeln('<td></td>')
    request.writeln('<td background="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"></td>')
    for i in range(len(tabdefs)):
      tabdef = tabdefs[i]
      tab = tabsdict[tabdef.id]
      request.writeln('<td background="' + join(WEB_PROGRAM_URL, 'tab-top.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-top.png') + '"></td>')
      if i == lasttab:
        request.writeln('<td background="' + join(WEB_PROGRAM_URL, 'tab-curve-end.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-curve-end.png') + '"></td>')
      else:
        request.writeln('<td background="' + join(WEB_PROGRAM_URL, 'tab-curve.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-curve.png') + '"></td>')
    request.writeln('<td></td>')
    request.writeln('</tr>')
    
    # main row
    request.writeln('<tr>')
    request.writeln('<td></td>')
    request.writeln('<td background="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"></td>')
    for i in range(len(tabdefs)):
      tabdef = tabdefs[i]
      tab = tabsdict[tabdef.id]
      if i == 0:
        request.writeln('<td noWrap id="' + tab.id + '" onClick="select(\'' + tabdef.id + '\', \'' + tab.id + '\', \'' + tabdef.view + '\')" bgcolor="#F4F4F4" class="tab" style="padding-left:8px">' + tabdef.name + '</td>')
      else:
        request.writeln('<td noWrap id="' + tab.id + '" onClick="select(\'' + tabdef.id + '\', \'' + tab.id + '\', \'' + tabdef.view + '\')" bgcolor="#F4F4F4" class="tab">' + tabdef.name + '</td>')
      if i == lasttab:
        request.writeln('<td background="' + join(WEB_PROGRAM_URL, 'tab-line-end.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-line-end.png') + '"></td>')
      else:
        request.writeln('<td background="' + join(WEB_PROGRAM_URL, 'tab-line.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-line.png') + '"></td>')
    request.writeln('<td></td>')
    request.writeln('</tr>')
    
    # footer row    
    request.writeln('<tr>')
    request.writeln('<td><img src="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"></td>')
    request.writeln('<td background="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"></td>')
    for i in range(len(tabdefs)):
      tabdef = tabdefs[i]
      tab = tabsdict[tabdef.id]
      request.writeln('<td background="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"></td>')
      if i == lasttab:
        request.writeln('<td background="' + join(WEB_PROGRAM_URL, 'tab-botright-end.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-botright-end.png') + '"></td>')
      else:
        request.writeln('<td background="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"></td>')
    request.writeln('<td width="100%" background="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"><img src="' + join(WEB_PROGRAM_URL, 'tab-dark.png') + '"></td>')
    request.writeln('</tr>')
    
    request.writeln('</table>')
    request.writeln('</html>')

    

  ################################################
  ###   Administrator functions for the view
    
  def initialize_activity(self, request, new_activity, tabdefs=[ ('Comments:', 'Commenter') ]):
    '''Called from the Administrator.  Sets up the activity.
       tabdefs is a list of tuples ( "tab name", "tab view" ) defining initial tabs for the view
    '''
    # set up the initial tabs
    for name, view in tabdefs:
      tab = datagate.create_item(creatorid=request.session.user.id, parentid=new_activity.id)
      tab.name = name
      tab.view = view
      tab.linkitemid = tab.id # default the link to myself
      tab.save()
      BaseView.views[tab.view.lower()].initialize_activity(request, tab)
     

  def send_admin_page(self, request):
    '''Sends an administrator page for this view.'''

    # send the html    
    request.writeln('''
      <script language='JavaScript' type='text/javascript'>
      <!--
        function editname(id, name) {
          var text = prompt("Edit item Name:", name);
          if (text != null && text != '') {
            text = encode(text);
            window.location.href = "''' + request.cgi_href(gm_action='TabPane.editname', itemid=item.id, activityid=None, activityname=None) + '''&activityid=" + id + "&activityname=" + text;
          }
        }
        
      //-->
      </script>
    ''')

    # item name
    request.writeln("<p><center><font size=+1>Edit " + self.title + ": " + item.name + "</font>")
    request.writeln("</center></p>")
    
    # activities in this item (top level records in the Items table)
    activities = datagate.get_child_items(item.id)
    if len(activities) == 0: previousid=''
    else: previousid = activities[-1].id
    request.writeln(request.cgi_form(gm_action='TabPane.addactivity', name=None, previousid='last', itemid=item.id, text=None, viewtype=None) + '''
      <center>
      <table border=1 cellspacing=0 cellpadding=5>
        <tr>
          <th>&nbsp;</th>
          <th>Activity</th>
          <th>Type</th>
          <th>Actions</th>
        </tr>
    ''')
    for i in range(len(activities)):
      activity = activities[i]
      request.writeln('<tr>')
      request.writeln('<td>&nbsp;' + str(i+1) + '.&nbsp;</td>')
      request.writeln('<td><a href="javascript:editname(\'' + activity.id + '\', \'' + decode(activity.name).replace("'", "\\'") + '\');">' + activity.name + '</a></td>')
      request.writeln('<td>' + BaseView.regular_components_dict[activity.view.lower()].NAME + '</td>')
      request.write('<td>')
      if i == 0: request.write('Up')
      else: request.write('<a href="' + request.cgi_href(itemid=item.id, gm_action='TabPane.moveactivity', activityid=activity.id, previousid=activities[i-1].get_previousid()) + '">Up</a>')
      request.write('&nbsp;|&nbsp;')
      if i == len(activities) - 1: request.write('Down')
      else: request.write('<a href="' + request.cgi_href(itemid=item.id, gm_action='TabPane.moveactivity', activityid=activity.id, previousid=activities[i+1].id) + '">Down</a>')
      request.write('&nbsp;|&nbsp;')
      request.write('<a href="' + request.cgi_href(itemid=activity.id, gm_action=None, view='Administrator', global_adminview=activity.view) + '">Edit</a>')
      request.write('&nbsp;|&nbsp;')
      request.write('''<a href="javascript:confirm_url('Delete this activity and *all* related data?', \'''' + request.cgi_href(itemid=item.id, gm_action='TabPane.delactivity', activityid=activity.id) + '''\');">Delete</a>''')
      request.writeln('</td>')
      request.writeln('</tr>')
    request.writeln('''
        <tr>
          <td>&nbsp;</td>
          <td><input type="text" name="name" value="New Activity" onfocus="clearField(this);"></td>
          <td>
            <select name="viewtype">
    ''')
    for activity_type in BaseView.regular_components:
      request.writeln('<option value="' + activity_type[0] + '">' + activity_type[1].NAME + '</option>')
    request.writeln('''
            </select>
          </td>
          <td align="center"><input type="submit" value="Add"></td>
        </tr>
      </table>
      </center>
      </form>
    ''')
    
    return item
    
    
  def editname_action(self, request):
    item = datagate.get_item(request.getvalue('itemid', ''))
    itemname = request.getvalue('activityname', '')
    if itemname != '':
      child = item.get_child(request.getvalue('activityid'))
      child.name = itemname
      child.save()
    
  def addactivity_action(self, request):
    item = datagate.get_item(request.getvalue('itemid', ''))
    # create the activity
    activity = datagate.create_item(creatorid=request.session.user.id, parentid=item.id, previousid='last')
    activity.name = request.getvalue('name', '')
    activity.view = request.getvalue('viewtype', '')
    activity.linkitemid = activity.id # default the link to myself (an analyzer can override this)
    activity.save()
    BaseView.views[activity.view.lower()].initialize_activity(request, activity)
    
  def delactivity_action(self, request):
    datagate.del_item(request.getvalue('activityid', ''))
    
  def moveactivity_action(self, request):
    item = datagate.get_item(request.getvalue('itemid', ''))
    activity = datagate.get_item(request.getvalue('activityid'))
    parent = activity.get_parent()
    parent.remove_child(activity)
    parent.insert_child(activity, request.getvalue('previousid'))
    parent.save()
        
