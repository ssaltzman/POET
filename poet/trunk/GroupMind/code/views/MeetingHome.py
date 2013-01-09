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
from Events import Event
import BaseView
import Directory
import datagate
import gzip
import sys, os.path
import xml.dom.minidom


meeting_components = [
  'analyzer',
  'blank',
  'commenter',
  'commenterreviser',
  'customfield',
  'gridview',
  'rating',
  'ratingproxy',
  'tabpane',
  'threader',
  'tree',
  'voter',
]


class MeetingHome(BaseView.BaseView):
  NAME = 'Collaborative Meeting'
  TOP_LEVEL_COMPONENT = 1
  REGULAR_COMPONENT = 0
  title = 'Meeting'
  rights_list = [ 'Show Activities Selector' ]
  
  def __init__(self):
    BaseView.BaseView.__init__(self)
    self.interactive = 1


  #####################################
  ###   Client view methods
     
  def send_content(self, request):
    '''Shows the main meeting window to the user (allows selection of activities)'''
    action = request.getvalue('_mhaction', '')
    if action == 'menu': 
      self.send_menu(request)
      
    else:
      self.send_frames(request)
    
    
  def send_frames(self, request):
    '''Sends the menu and content frames'''
    request.writeln(HTML_HEAD_NO_CLOSE)
    request.writeln('''
      <script language='JavaScript' type='text/javascript'>
      <!--
        function processSelect(itemid) {
          var sel = menu.document.getElementById("activityid");
          if (sel.value != itemid) {
            alert('The moderator has moved participants to a new activity.');
            sel.value = itemid;
            menu.selectActivity(); // it doesn't trigger the event automatically
          }
        }
      //-->
      </script>
      </head>
    ''')
    request.writeln("<frameset border='1' rows='30, *'>")
    request.writeln("<frame marginheight='0' marginwidth='0' name='menu' src='" + request.cgi_href(global_meetingid=request.getvalue('global_rootid', ''), _mhaction='menu') + "'>")
    request.writeln("<frame marginheight='0' marginwidth='0' name='activity' src='" + request.cgi_href(global_meetingid=request.getvalue('global_rootid', ''), global_view='Blank') + "'>")
    request.writeln("</frameset>")
    request.writeln("</html>")    
    
  
  
  
  def send_menu(self, request):
    '''Sends the menu'''
    meeting = Directory.get_meeting(request.getvalue('global_rootid', ''))
    activities_item = meeting.search1(name='activities')
    activities = datagate.get_child_items(activities_item.id)
    rights = self.get_user_rights(request)

    request.writeln(HTML_HEAD_NO_CLOSE + '''
      <script language='JavaScript' type='text/javascript'>
      <!--
        var views = new Array();
    ''')
    for activity in activities:
      request.writeln('        views["' + activity.id + '"] = "' + activity.view + '";')
    request.writeln('''        
        function selectActivity() {
          var activityid = document.getElementById('activityid').value;
          parent.activity.location.href = "''' + request.cgi_href(global_windowid=request.getvalue('global_windowid', ''), global_view=None, global_rootid=None, frame=None) + '''&global_view=" + views[activityid] + "&global_rootid=" + activityid;
        }
        
        function initialLoad() {
          selectActivity();
        }
        
        function openHelp() {
          window.open("''' + WEB_PROGRAM_URL + '''Help/", "helpwindow", "dependent,height=400,width=300,scrollbars,resizable");
          return false;
        }
        
        function gotoActivity(activityid, requester_sessionid) {
          var activity = document.getElementById('activityid');
          if ("''' + request.session.id + '''" != requester_sessionid) {
            activity.value = activityid;
            selectActivity();
          }else{
            alert("The sync message has been sent to all participants in this meeting.");
          }
        }

        function syncParticipants() {
          if (confirm("Syncronize this meeting's participants to this activity?")) {
            var activityid = document.getElementById('activityid').value;
            sendEvent('gotoActivity', activityid, "''' + request.session.id + '''");
          }
        }
        
      //-->
      </script>
      </head>      
    
      <body background="''' + join(WEB_PROGRAM_URL, "background1.png") + '''" onload="initialLoad();">
      <table border=0 cellspacing=3 cellpadding=0 width=100%><tr><td nowrap valign="center" align="left" style="color:#FFFFFF; font-weight:800">
        ''' + html(meeting.name) + ''': ''' + html(request.session.user.name) + '''
      </td><td nowrap align="center" style="color:#FFFFFF">
    ''')

    if rights['Show Activities Selector'] or request.session.user.superuser == '1': # don't show unless there are more than one or the superuser
      request.writeln('''
        Activity:
        <select name="activityid" id='activityid' onchange="javascript:selectActivity()">
      ''')
      for activity in activities:
        request.writeln('<option value="' + activity.id + '">' + activity.name + '</option>')
      request.writeln('</select>')
      if request.session.user.superuser == '1':
        request.writeln('<input type="button" value="Sync Participants" onclick="javascript:syncParticipants();">')
    
    else: 
      # this hidden input allows the selectActivity() js functions to work (called with body.onLoad)
      request.writeln('<input type="hidden" name="activityid" id="activityid" value="' + activities[0].id + '">')

    request.writeln('</td><td align="right" style="color:#FFFFFF">')
    if request.session.user.superuser == '1':
      request.writeln('<a style="color:white" target="_top" href="' + request.cgi_href(itemid=meeting.id, global_view='Administrator', global_adminview='MeetingHome') + '">Administrator</a> | ')
    request.writeln('''
        <a style='color:white' onclick='javascript:openHelp();'>Help</a>
        | 
        <a target="_top" href="''' + request.cgi_href(global_view='logout') + '''" style="color:white">Logout</a>
      </td></tr></table>
      <script language='JavaScript' type='text/javascript'>startEventLoop();</script>
      </body></html>
    ''')

  
  def gotoActivity_action(self, request, activityid, requester_sessionid):
    return Event('gotoActivity', activityid, requester_sessionid)


  ################################################
  ###   Administrator functions for the view
    
  def send_admin_page(self, request):
    '''Sends an administrator page for this view.'''

    # process all data change actions
    try:
      meeting = self.process_admin_actions(request)
      if meeting.view =='strikecom': #short circut if we are loading a strikecom game
        request.writeln('''
          <script language='JavaScript' type='text/javascript'>
          <!--
            window.location.href = "'''+request.cgi_href(global_meetingid=meeting.id, global_view='Administrator', global_adminview="StrikeCom", itemid=meeting.id)+'''";
          //-->
          </script>
        ''')
        return
      
    except Exception, e:
      request.writeln('<b><font color="#FF0000">' + str(e) + '</font></b>')
      return

    # send the html    
    request.writeln('''
      <script language='JavaScript' type='text/javascript'>
      <!--
        function editname(id, name) {
          var text = prompt("Edit Item Name:", name);
          if (text != null && text != '') {
            text = encode(text);
            window.location.href = "''' + request.cgi_href(global_meetingid=meeting.id, _mhaction='editname', itemid=meeting.id, activityid=None, activityname=None) + '''&activityid=" + id + "&activityname=" + text;
          }
        }
        
        function addGroup() {
          var text = prompt("New Group Name:");
          if (text != null && text != '') {
            text = encode(text);
            window.location.href = "''' + request.cgi_href(global_meetingid=meeting.id,_mhaction='addgroup', itemid=meeting.id, name=None) + '''&name=" + text;
          }
        }
        
      //-->
      </script>
    ''')

    # item name
    request.writeln("<p><center><font size=+1>Edit " + self.title + ": " + html(meeting.name) + "</font>")
    request.writeln("</center></p>")
    request.writeln("<p>&nbsp;</p>")
    
    # main table with the two columns
    request.writeln('<table border=0 width=100%><tr><td width="50%" valign="top">')
    
    # groups in this meeting
    groups_item = meeting.search1(name='groups')
    groups = datagate.get_child_items(groups_item.id)
    allusers = Directory.get_users()
    allusers.sort(lambda a,b: cmp(a.username, b.username))
    request.writeln('''
      <center>
      <b>Meeting Groups:</b>
      <div align="right"><a href="javascript:addGroup()">Add New Group</a></div>
      <table border=1 cellspacing=0 cellpadding=5 width="100%">
        <tr>
          <th>Name</th>
          <th>Users</th>
          <th>Actions</th>
        </tr>
    ''')
    for group in groups:
      groupusers = [ Directory.get_user(child.user_id) for child in group.get_child_items() ]
      groupusers.sort(lambda a,b: cmp(a.username, b.username))
      request.writeln('<tr>')
      request.writeln('<td valign="top">' + html(group.name) + '</td>')
      request.writeln('<td>')
      request.writeln(request.cgi_form(_mhaction='groupusers', global_meetingid=meeting.id, _allusers=None, _groupusers=None, _groupid=None))
      request.writeln('<input type="hidden" name="_groupid" value="' + group.id + '">')
      request.writeln('<table border=0 cellspacing=0 cellpadding=0><tr><td>')
      request.writeln('All Users:<br>')
      request.writeln('<select size="10" name="_allusers" multiple>')
      for user in allusers:
        if not user in groupusers:
          request.writeln('<option value="' + user.id + '">' + html(user.name) + '</option>')
      request.writeln('</select>')
      request.writeln('</td><td>')
      request.writeln('<p><input type="submit" value="->" name="submit"></p>')
      request.writeln('<p><input type="submit" value="<-" name="submit"></p>')
      request.writeln('</td><td>')
      request.writeln('Group Members:<br>')
      request.writeln('<select size="10" name="_members" multiple>')
      for user in groupusers:
        request.writeln('<option value="' + user.id + '">' + html(user.name) + '</option>')
      request.writeln('</select>')
      request.writeln('</td></tr></table>')
      request.writeln('</form>')
      request.writeln('</td>')
      request.writeln('''<td valign="top"><a href="javascript:confirm_url('Delete this group and remove users from the meeting?', \'''' + request.cgi_href(global_meetingid=meeting.id, itemid=meeting.id, _mhaction='delgroup', groupid = group.id) + '''\');">Delete</a></td>''')
      request.writeln('</tr>')
    request.writeln('''
      </table>
      </center>
    ''')    
    
    # go to the second column of the main, two-columned table
    request.writeln('</td><td width="50%" valign="top">')
    
    # activities in this meeting
    activities_item = meeting.search1(name='activities')
    activities = datagate.get_child_items(activities_item.id)
    if len(activities) == 0: previousid=''
    else: previousid = activities[-1].id
    request.writeln(request.cgi_form(global_meetingid=meeting.id, _mhaction='addactivity', name=None, previousid=previousid, itemid=meeting.id, text=None, viewtype=None) + '''
      <center>
      <b>Meeting Activities:</b>
      <div align="right">&nbsp;</div>
      <table border=1 cellspacing=0 cellpadding=5 width="100%">
        <tr>
          <th>&nbsp;</th>
          <th>Activity</th>
          <th>Type</th>
          <th>Actions</th>
        </tr>
    ''')
    for i in range(len(activities)):
      activity = activities[i]
      view = BaseView.views[activity.view]
      request.writeln('<tr>')
      request.writeln('<td>&nbsp;' + str(i+1) + '.&nbsp;</td>')
      request.writeln('<td><a href="javascript:editname(\'' + activity.id + '\', \'' + html(activity.name).replace("'", "\\'") + '\');">' + activity.name + '</a></td>')
      request.writeln('<td>' + view.NAME + '</td>')
      request.write('<td>')
      if i == 0: request.write('Up')
      else: request.write('<a href="' + request.cgi_href(global_meetingid=meeting.id, itemid=meeting.id, _mhaction='moveactivity', activityid=activity.id, previousid=activities[i-1].get_previousid()) + '">Up</a>')
      request.write('&nbsp;|&nbsp;')
      if i == len(activities) - 1: request.write('Down')
      else: request.write('<a href="' + request.cgi_href(global_meetingid=meeting.id, itemid=meeting.id, _mhaction='moveactivity', activityid=activity.id, previousid=activities[i+1].id) + '">Down</a>')
      request.write('&nbsp;|&nbsp;')
      request.write('<a href="' + request.cgi_href(global_meetingid=meeting.id, itemid=activity.id, _mhaction=None, global_view='Administrator', global_adminview=activity.view) + '">Edit</a>')
      request.write('&nbsp;|&nbsp;')
      request.write('''<a href="javascript:confirm_url('Delete this activity and *all* related data?', \'''' + request.cgi_href(global_meetingid=meeting.id, itemid=meeting.id, _mhaction='delactivity', activityid=activity.id) + '''\');">Delete</a>''')
      request.writeln('</td>')
      request.writeln('</tr>')
    request.writeln('''
        <tr>
          <td>&nbsp;</td>
          <td><input type="text" name="name" value="New Activity" onfocus="clearField(this);"></td>
          <td>
            <select name="viewtype">
    ''')
    for name in meeting_components:
      view = BaseView.views[name]
      request.writeln('<option value="' + name + '">' + html(view.NAME) + '</option>')
    request.writeln('''
            </select>
          </td>
          <td align="center"><input type="submit" value="Add"></td>
        </tr>
      </table>
      </center>
      </form>
    ''')
    
    request.writeln('</td></tr></table>')
    
    # send the group rights
    request.writeln('<p><center>')
    self.send_admin_rights(request, meeting, meeting)
    request.writeln('</center>')
    
    
    
  def process_admin_actions(self, request):
    '''Process all item actions'''
    meeting = datagate.get_item(request.getvalue('global_meetingid', ''))
    action = request.getvalue('_mhaction', '')
    if action == 'copyitem':
      meeting = datagate.copy_deep(request.getvalue('_copyitemid', ''), Directory.meetings_item.id)
      meeting.name = request.getvalue('_itemname', '')
      meeting.save()
      return meeting
      
    elif action == 'import':
      try:
        importfile = request.form['subaction']
        gz = gzip.GzipFile(importfile.filename, 'r', fileobj=importfile.file)
        doc = xml.dom.minidom.parse(gz)
        
      except IOError:
        raise IOError, 'An error occurred while importing the file.  Are you sure it is a gzipped XML document (exported from GroupMind)?'
      return Directory.import_meeting(doc, request.session.user.id)

    activities_item = meeting.search1(name='activities')
    groups_item = meeting.search1(name='groups')
    if action == 'editname':
      itemname = request.getvalue('activityname', '')
      if itemname != '':
        child = activities_item.get_child(request.getvalue('activityid'))
        child.name = itemname
        child.save()
    
    elif action == 'addactivity':
      # create the activity
      name = request.getvalue('name', '')
      if name != '':
        activity = datagate.create_item(creatorid=request.session.user.id, parentid=activities_item.id)
        activity.name = name
        activity.previousid = request.getvalue('previousid', '')
        activity.view = request.getvalue('viewtype', '')
        activity.save()
        
        # allow the activity view to initialize itself
        BaseView.views[activity.view.lower()].initialize_activity(request, activity)

    elif action == 'delactivity':
      datagate.del_item(request.getvalue('activityid', ''))
      
    elif action == 'moveactivity':
      activity = datagate.get_item(request.getvalue('activityid'))
      parent = activity.get_parent()
      parent.remove_child(activity)
      parent.insert_child(activity, request.getvalue('previousid'))
      parent.save()
      
    elif action == 'addgroup':
      name = request.getvalue('name', '')
      if name != '':
        group = datagate.create_item(creatorid=request.session.user.id, parentid=groups_item.id)
        group.name = name
        group.save()
        
    elif action == 'delgroup':
      datagate.del_item(request.getvalue('groupid', ''))

    elif action == 'groupusers':
      submit = request.getvalue('submit', '')
      group = groups_item.get_child(request.getvalue('_groupid', ''))
      if submit == '->':
        group_users = [ child.user_id for child in group.get_child_items() ]
        for user_id in request.getlist('_allusers'):
          if not user_id in group_users:
            child = datagate.create_item(creatorid=request.session.user.id, parentid=group.id)
            child.user_id = user_id
            child.save()
      
      elif submit == '<-':
        for user_id in request.getlist('_members'):
          for child in group.get_child_items():
            if child.user_id == user_id:
              datagate.del_item(child.id)
              break
              
    # finally, return the meeting (since we might have created it here)          
    return meeting


  def initialize_activity(self, request, meeting):
    '''Called from the Administrator.  Sets up the activity'''
    BaseView.BaseView.initialize_activity(self, request, meeting)
    activities = datagate.create_item(creatorid=request.session.user.id, parentid=meeting.id)
    activities.name='activities'
    activities.save()
    

