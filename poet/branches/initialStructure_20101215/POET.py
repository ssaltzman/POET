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
import smtplib


meeting_components = [
  'questioneditor',
  'questionasker',
  'reportfindings',
  'commenter'
]


class POET(BaseView.BaseView):
  NAME = 'POET Acquisition Collaboration'
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
    request.writeln("<frameset border='0' rows='60px, *'>")
    request.writeln("<frame marginheight='0' marginwidth='0' name='menu' src='" + request.cgi_href(global_meetingid=request.getvalue('global_rootid', ''), _mhaction='menu') + "'>")
    request.writeln("<frame id='activityFrame' marginheight='0' marginwidth='0' name='activity' src='" + request.cgi_href(global_meetingid=request.getvalue('global_rootid', ''), global_view='Blank') + "'>")
    request.writeln("</frameset>")
    request.writeln("</html>")     
  
  def send_menu(self, request):
    '''Sends the menu'''
    meeting = Directory.get_meeting(request.getvalue('global_rootid', ''))
    activities_item = meeting.search1(name='activities')
    activities = datagate.get_child_items(activities_item.id)
    log.info("Meeting<br/>" + str(meeting) + "<br/>Activities<br/>" + str(activities))
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
          window.open("''' + WEB_PROGRAM_URL + '''/Help/", "helpwindow", "dependent,height=800,width=1000,scrollbars,resizable");
          return false;
        }
	
	function openProgInfo() {
          window.open("''' + WEB_PROGRAM_URL + '''/ProgInfo/", "proginfowindow", "dependent,height=800,width=1000,scrollbars,resizable");
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
    
      <body id="menu" ''" onload="initialLoad();" style="margin:0;padding:0;">
      <table cellspacing="0"  style="border-bottom:#99ccff 1px dotted;padding:3px;">
      	<tr>
      		<td id="menu-logo">
      			<div id="poet-logo">POET</div>
      		</td>
      	<td id="menu-activities">
    ''')

    user_is_pm = 0
    for child in meeting:
      if child.name == "groups":
        for group in child:
          if group.name == "PM":
            for pm_item in group:
              if pm_item.user_id == request.session.user.id:
                user_is_pm = 1

    if rights['Show Activities Selector'] or request.session.user.superuser == '1' or user_is_pm == 1: # don't show unless there are more than one or the superuser
      request.writeln('''
        <div class="hide">Activity:
        <select name="activityid" id='activityid' onchange="javascript:selectActivity()">
      ''')
      for activity in activities:
        request.writeln('<option value="' + activity.id + '">' + activity.name + '</option>')
      request.writeln('</select>')
      if request.session.user.superuser == '1':
        request.writeln('<input type="button" value="Sync Participants" onclick="javascript:syncParticipants();"></div>')

    # select activity based on meeting status
    elif meeting.status < 2: #results not released -- send to QuestionAsker
      # this hidden input allows the selectActivity() js functions to work (called with body.onLoad)
      request.writeln('<input type="hidden" name="activityid" id="activityid" value="' + activities[1].id + '">')
    else: #results released -- send to Findings
      request.writeln('<input type="hidden" name="activityid" id="activityid" value="' + activities[2].id + '">')

    request.writeln('</td><td id="user-menu">')
    request.writeln('logged in as <strong>' + html(request.session.user.name) + '</strong>')
    if request.session.user.superuser == '1' or user_is_pm == 1:
      request.writeln('<span class="divider">|</span> <a target="_top" href="' + request.cgi_href(itemid=meeting.id, global_view='Administrator', global_adminview='POET') + '">Manage Program</a>')
    request.writeln('''
	<span class="divider">|</span> <a onclick='javascript:openProgInfo();'>Program Information</a>	    
        <span class="divider">|</span> <a onclick='javascript:openHelp();'>Help</a> <span class="divider">|</span> 
        <a target="_top" href="''' + request.cgi_href(global_view='logout') + '''" >Logout</a>
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

    length = 0
    percentage = 0

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

        function openMeeting(id, view) {
          window.location.href="''' + request.cgi_href(global_rootid=None, global_view=None) + '''&global_rootid=" + id + "&global_view=" + view;
        }
        ''')
    #meeting = Directory.get_meeting(request.getvalue('global_rootid', ''))
    activities_item = meeting.search1(name='activities')
    activities = datagate.get_child_items(activities_item.id)
    assessmentId   = ""
    assessmentView = ""
    for activity in activities:
      if activity.name == "Findings":
        assessmentId   = activity.id
        assessmentView = activity.view
      if activity.name == "Question Editor":
        sets = activity.search1(name="sets")
        groupMapping = activity.search1(name="groupMapping")
        userAnswers = activity.search1(name="userAnswers")
      if activity.name == "Assessment":
        surveyId   = activity.id
        surveyView = activity.view
      if activity.name == "Commenter":
        brainstormId  = activity.id
        brainstormView = activity.view
    request.writeln('''
        var views = new Array();
    ''')

    request.writeln('''
        function openResults(id, view, page) {
          var activityid; 
          var activityview;
          if(page == "results"){
            activityid = "'''+assessmentId+'''";
            activityview = "'''+assessmentView+'''";
          }
          else if (page == "survey"){
            activityid = "'''+surveyId+'''";
            activityview = "'''+surveyView+'''";
          }
	  else if (page == "brainstorm"){
            activityid = "'''+brainstormId+'''";
            activityview = "'''+brainstormView+'''";
          }
          window.location.href = "''' + request.cgi_href(global_windowid=request.getvalue('global_windowid', ''), global_view=None, global_rootid=None, frame=None) + '''&global_view=" + activityview + "&global_rootid=" + activityid;
        }
         
      //-->
      </script>
    ''')

    request.writeln('''<script src="''' + join(WEB_PROGRAM_URL, 'jquery-1.4.2.min.js') + '''"></script>''')
    request.writeln('''<script src="''' + join(WEB_PROGRAM_URL, 'jquery-ui-1.8.2.custom.min.js') + '''"></script>''')
    request.writeln('''<script src="''' + join(WEB_PROGRAM_URL, 'multiSelect.js') + '''"></script>''')
    request.writeln('''<link href="''' + join(WEB_PROGRAM_URL, 'jquery-ui-1.8.2.custom.css') + '''" rel="stylesheet" type="text/css"/>''')
    request.writeln('''<script src="''' + join(WEB_PROGRAM_URL, 'superfish.js') + '''"></script>''')
    request.writeln('''<link href="''' + join(WEB_PROGRAM_URL, 'superfish.css') + '''" rel="stylesheet" type="text/css"/>''')

    request.writeln('''
    <script type="text/javascript">
	$(function() {
		$("input:button").button();
		$("input:submit").not(".swapSet").button();
	});

        function saveUsers(fromGroup, toGroup, users){
          document.getElementById('fromGroup').value = fromGroup;
          document.getElementById('toGroup').value = toGroup;
          document.getElementById('changedUsers').value = users;

          document.userChange.submit();
        }

        
        
    </script>

    ''')
    
    # userEdit div
    request.writeln('<div id="editPage" style="width:100%;">')
    
    request.writeln("<center><h1>" + html(meeting.name) + "</h1></center>")
    
    if meeting.status == 2:
      request.writeln('''<div id="notification" class="ui-state-highlight ui-corner-all" style="width:854px;margin: 10px 0px 10px 200px; padding: 10px 20px;display:block;"> 
				<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: 1em;"></span>
				<strong>Results have been released to users successfully</strong></p>
			  </div>
      ''')
    else:
      request.writeln('''<div id="notification" class="ui-state-highlight ui-corner-all" style="width:854px;margin: 10px 0px 10px 200px; padding: 10px 20px;display:none;"> 
				<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>
				<strong>Results have been released to users successfully</strong></p>
			  </div>
      ''')
    
    # groups in this meeting - drag and drop area
    groups_item = meeting.search1(name='groups')
    groups = datagate.get_child_items(groups_item.id)
    allusers = Directory.get_users()
    allusers.sort(lambda a,b: cmp(a.username, b.username))
    
    request.writeln('''
    <div id="content" class="assign-user-groups">
      <div class='panel'>
    ''')

    # if there's an open set, don't let the PM release the results
    openSet = False
    for group in groups:
      if not group.sets == '':
        openSet = True
        break
    
    request.writeln('''
        <div id="buttonControls" >
          <br/><input class="butControls" type="button" value="Edit Questions" onClick='openMeeting("'''+meeting.id+'''", "'''+meeting.view+'''")'><br/>
          <input class="butControls" type="button" value="View Results" onClick='openResults("'''+meeting.id+'''", "'''+meeting.view+'''", "results")'><br/>
	  <input class="butControls" type="button" value="Brainstorm" onClick='openResults("'''+meeting.id+'''", "'''+meeting.view+'''", "brainstorm")'>
          '''+request.cgi_form(_mhaction='results'))
    if openSet:
      request.writeln('''<input class="butControls" type="submit" value="Release Results" disabled />''')
    else:
      request.writeln('''<input class="butControls" type="submit" value="Release Results" onclick="document.getElementById('notification').style.display='block';"  />''')
    request.writeln('</form>')
    if not request.session.user.superuser == '1':
      request.writeln('''<a href="mailto:poetList@mitre.org?subject=Survey%20Questions%20Released&body=The%20questions%20in%20the%20survey%20has%20been%20released%20to%20you.%20Please%20login%20to%20take%20the%20survey.">''')
      request.writeln('''<input class="butControls" type="button" value="Email Users"><br/></a>''')
      request.writeln('''<input class="butControls" type="button" value="Take Survey" onClick='openResults("'''+meeting.id+'''", "'''+meeting.view+'''", "survey")'><br/>''')
    request.writeln('''</div> <!-- /#buttonControls --> ''')
    
    if request.session.user.superuser == '1':
      request.writeln('''
	<div id="userAssignment">
        <h2>Unassigned Users</h2>
        <p class="selector">Select:
          <a href='#' onclick='return $.dds.selectAll("unassigned_list");'>all</a>
          <a href='#' onclick='return $.dds.selectNone("unassigned_list");'>none</a>
          <a href='#' onclick='return $.dds.selectInvert("unassigned_list");'>invert</a>
        </p>
        <div class="draggable">
          <ul id="unassigned_list">''')
      assignedUsers = [] #list of ids
      for group in groups:
        for user in group:
          if not user.user_id in assignedUsers:
            assignedUsers.append(user.user_id)

      unassignedUsers = [user for user in allusers if user.id not in assignedUsers] #equivalent to iteratering through allusers and 
      for user in unassignedUsers:                                                  #then checking "if not user.id in assignedUsers" for each
        #if not user.id in assignedUsers:
        request.writeln('<li class="draggable" id="' + user.id + '">' + html(user.name) + '</li>')
    
      request.writeln('''
          </ul>
        </div><!-- .draggable -->
	</div> <!-- #/userAssignment -->
      ''')
    
    request.writeln('''
      </div><!-- /#panel -->
    </div><!-- /#content -->
    ''')
    request.writeln('''<table class="user-table" cellspacing="0">
        <tr class="table-header">
          <td>Group
    ''')
    if request.session.user.superuser == '1':
      request.writeln('''<a href="javascript:addGroup()">Add New Group</a>''')
    request.writeln('''
	  </th>
    ''')
    request.writeln('''<td>Users</th>''')
    request.writeln('''
          <td>Sets</th>
        </tr>
    ''')
    for group in groups:
      groupusers = [ Directory.get_user(child.user_id) for child in group.get_child_items() ]
      groupusersId = [user.id for user in groupusers]
      groupusers.sort(lambda a,b: cmp(a.username, b.username))
      request.writeln('<tr>')
      request.writeln('<td class="' + html(group.name) + '_td"><h2>' + html(group.name))
      if request.session.user.superuser == '1':
        request.writeln(''' <a class="title-delete" href="javascript:confirm_url('Delete this group and remove users from the meeting?', \'''' + request.cgi_href(global_meetingid=meeting.id, itemid=meeting.id, _mhaction='delgroup', groupid = group.id) + '''\');">Delete</a>''')        
      request.writeln('</h2><br/>')            
      request.writeln('<div class="pct-done" style="height:70px;width:88%">')
      usersMessage = str(len(groupusers)) + ' user'
      if not (len(groupusers)) == 1:
        usersMessage = usersMessage + 's'
      usersMessage = usersMessage + '<br/>'
      #request.writeln(str(len(groupusers)) + ' users<br/>')
      if groupusers == []: #empty group
        request.writeln('No users in this group.<br/>')
      elif group.sets == "": #no sets have been asked to a non-empty group
        request.writeln(usersMessage)
        request.writeln('No open sets.<br/>')
      else: #sets have been asked to a non-empty group
        request.writeln(usersMessage)
        quesIDlist = []
        numInProgress = 0
        numOfFinished = 0
        for groupMap in groupMapping:
          if groupMap.name == group.name:
            for child in groupMap:
              if child.name == "quesId":
                quesIDlist = child.quesId
                break
            break
        setFilter = [] #this will be all quesIDs that belong to the Asked sets
        for item in sets:
          if item.name in group.sets:
            for child in item:
              if child.name == "quesId":
                setFilter.extend(child.quesId) 
        setFilter = list(set(setFilter)) #Removes duplicates. This isn't necessary, but I think the time spent here will be saved...
        for element in quesIDlist[:]: 
          if not element in setFilter: #...when we repeatedly traverse setFilter down here.
            quesIDlist.remove(element)
        request.writeln(str(len(quesIDlist))+" total questions.<br/>")
        if len(quesIDlist) > 0:
          for child in userAnswers: #iterate over the users
            if child.creatorid in groupusersId:
              answeredQuestions = 0
              for answer in child:
                if answer.questionId in quesIDlist:
                  answeredQuestions += 1
              if answeredQuestions == len(quesIDlist):
                numOfFinished += 1
              elif answeredQuestions > 0:
                numInProgress += 1
	  '''
          if numInProgress == 1:
            progressVerb = " person is"
          else:
            progressVerb = " people are"
          if numOfFinished == 1:
            endVerb = " person has"
          else:
            endVerb = " people have"
	  '''
          request.writeln(str(((numInProgress * 100) / len(groupusers)))+"% of users are in-progress.</br>")
          request.writeln(str(((numOfFinished * 100)/len(groupusers)))+"% of users are finished.")

      request.writeln('</div>')
      request.writeln('</td')
      request.writeln('</td')
      
      request.writeln('<td>')
      enableDroppage = ((group.sets == '') and request.session.user.superuser == '1')
      if (enableDroppage):
        request.writeln('''
            <div class="draggable">
              <ul id="''' + group.id + '''" >
          ''')
        for user in groupusers:
            request.writeln('<li class="draggable" id="' + user.id + '">' + str(user.name) + '</li>')
      else:
        request.writeln('''
            <div class="draggable">
              <ul class="locked" id="''' + group.id + '''" onload="disableDrop()">
          ''')
        for user in groupusers:
          request.writeln('<li id="' + user.id + '">' + str(user.name) + '</li>')        
      request.writeln('''</ul></div>''')  
      if (not enableDroppage):
        request.writeln('''<script type="text/javascript">$("#''' + group.id + '''").droppable({ disabled: true })</script>''')  
      request.writeln('</td>')
      
      

      #sets
      request.writeln('<td>')
      request.writeln(request.cgi_form(_mhaction='addset', groupid=group.id, setsid=sets.id, name='switchSets_'+ group.name))
      if group.sets == '':
        setList = []
        for item in sets:
          setList.append(item.name)
        request.writeln('<table class="set-list">')
	count = 0
        for item in setList:
          request.writeln('<td class="setCheckboxes"><input type="checkbox" id="'+str(group.name)+str(item)+'_cb" name="'+str(item)+'_cb" class="'+str(group.name)+'_cb" /><label for="'+str(item)+'_cb"> '+str(item)+'</label></td>')
	  count += 1
	  if count == 3:
	    request.writeln('</tr><tr>')
	    count = 0
	request.writeln('</tr></table>')
        #request.writeln('''<div class="setControls"><input type="submit" value="Ask" name="submit" /><input type="submit" value="Close" /></div>''')
	request.writeln('''<div class="setControls"><input type="image" class="closedSet" src="'''+join(WEB_PROGRAM_URL, 'switch.png')+'''" value="closed" alt="Submit" name="switchSet" id="switch_'''+ group.name + '''" onclick='document.getElementById("switch_'''+ group.name+'''").style.marginLeft="0px";document.getElementById("switch_'''+ group.name+'''").value="released";' /></div>''')
      else:
        setList = group.sets
        request.writeln('<select name="'+group.name+'Set" id="'+group.name+'Set" multiple disabled>')
        for item in setList:
          request.writeln('<option value="'+str(item)+'">'+str(item)+'</option>')
        request.writeln('</select>')  
        request.writeln('''<div class="setControls"><input type="image" class="releasedSet" src="'''+join(WEB_PROGRAM_URL, 'switch.png')+'''" value="released" alt="Submit" name="switchSet" id="switch_'''+ group.name + '''" onclick='document.getElementById("switch_'''+ group.name+'''").style.marginLeft="-93px";document.getElementById("switch_'''+ group.name+'''").value="closed";' /></div>''')
      request.writeln('</form>')
      request.writeln('</td>')
      request.writeln('</tr>')
    request.writeln('''</table>
      </div> <!-- /#userEdit -->
    ''')

    request.writeln(request.cgi_form(_mhaction='groupusers', global_meetingid=meeting.id, users=None, fromGroup=None, toGroup=None, name='userChange'))
    request.writeln('<input type="hidden" id="fromGroup" name="fromGroup" value="NOGROUP"><input type="hidden" id="toGroup" name="toGroup" value="NOGROUP"><input type="hidden" id="changedUsers" name="users" value="NOUSERS">')
    request.writeln('</form>')
        
  def process_admin_actions(self, request):
    '''Process all item actions'''
    meeting = datagate.get_item(request.getvalue('global_meetingid', ''))
    action = request.getvalue('_mhaction', '')

    if action == 'copyitem':
      meeting = datagate.copy_deep(request.getvalue('_copyitemid', ''), Directory.meetings_item.id)
      meeting.name = request.getvalue('_itemname', '')
      meeting.save()
      return meeting

    #elif action == 'publish':
    #handled by Ask

    elif action == 'results':
      meeting.status = 2
    
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
      fromGroup = request.getvalue('fromGroup', '')
      toGroup = request.getvalue('toGroup', '')
      users = request.getvalue('users', '').split()

      if not fromGroup == "unassigned_list":
        for c in datagate.get_child_items(fromGroup):
          for u in users:
            if c.user_id == u:
              datagate.get_item(fromGroup).remove_child(c)
      if not toGroup == "unassigned_list":
        for u in users:
          child = datagate.create_item(creatorid=request.session.user.id, parentid=toGroup)
          child.user_id = u
          child.save()

    elif action == 'addset':
      groupid = request.getvalue('groupid', '')
      group = datagate.get_item(groupid)
      submit = request.getvalue('switchSet', '')
      
      if submit == 'released':
        for user in group:
          user_data = datagate.get_item(user.user_id)
          user_data.answeredQuestions = [] #whenever a set is released/closed, wipe the list of backtrackable-questions
          user_data.backtrack = 0
          user_data.initialize = True
          user_data.save()
        meeting.status = 1
        creator = request.session.user 

        activities_item = meeting.search1(name='activities')
        root = activities_item.search1(name="Question Editor")
        questions = root.search1(name="questions")
        groupMapping = root.search1(name="groupMapping")

        d = {} #dictionary -- for binding dynamic variable names to values
        for g in groupMapping:
          listName = (str(g.name) + "IDlist").replace(' ', '') #replace -- removes spaces
          d[listName] = []

        sets = root.search1(name="sets")
        d2 = {} #dictionary -- for binding dynamic variable names to values
        for s in sets:
          listName2 = (str(s.name) + "IDlist").replace(' ', '') #replace -- removes spaces
          d2[listName2] = []

        for q in questions:
          if not q.delete:
            userGroups = q.users
            for u in userGroups:
              for g in groupMapping:
                if u == g.name:
                  listName = (str(g.name) + "IDlist").replace(' ', '')
                  (d[listName]).append(q.id)

            allSets = q.search1(name="sets")       
            for t in  allSets.get_child_items(self):
              for s in sets:
                if s.name == t.name:
                  listName2 = (str(s.name) + "IDlist").replace(' ', '')
                  (d2[listName2]).append(q.id)

        for g in groupMapping:
          children = g.get_child_items(self)
          if not children:
            p = datagate.create_item(creatorid=creator.id, parentid=g.id)
            p.name = 'percent'
            p.percent = 0
            p.save()
            ques = datagate.create_item(creatorid=creator.id, parentid=g.id)
            ques.name = 'quesId'
          else:
            ques = g.search1(name='quesId')

          listName = (str(g.name) + "IDlist").replace(' ', '')
          ques.quesId = d[listName]
          ques.save()

        for s in sets:
          childs = s.get_child_items(self)
          if not childs:
            questions = datagate.create_item(creatorid=creator.id, parentid=s.id)
            questions.name = "quesId"
          else:
            questions = s.search1(name='quesId')

          listName2 = (str(s.name) + "IDlist").replace(' ', '')
          questions.quesId = d2[listName2]
          questions.save()
      
        setsid = request.getvalue('setsid', '')
        sets = datagate.get_item(setsid)
        setList = []
        for item in sets:
          cbname = item.name + "_cb"
          cb = request.getvalue(cbname, '')
          if cb == "on":
            setList.append(item.name)
        if setList == []:
          group.sets = ''
        else:
          group.sets = setList 
      else:
        group.sets = ''
      group.save()
    # finally, return the meeting (since we might have created it here)          
    return meeting
  
  def send_email(self):
    sender = 'poetsystem@gmail.com'
    receivers = ['alissa@mitre.org']
    message = """From: POET System <poetsystem@gmail.com>
    To: Alissa Cooper <alissa@mitre.org>
    Subject: E-mail test
    
    This is a test e-mail message.
    """
    try:
      smtpObj = smtplib.SMTP('smtp.gmail.com', 465)
      smtpObj.sendmail(sender, receivers, message)
      log.info("Successfully sent email")
    except smtplib.SMTPException:
      log.info("Error: unable to send email")
    return

  def initialize_activity(self, request, meeting):
    '''Called from the Administrator.  Sets up the activity'''
    BaseView.BaseView.initialize_activity(self, request, meeting)
    activities = datagate.create_item(creatorid=request.session.user.id, parentid=meeting.id)
    activities.name='activities'
    activities.save()
    
    editor = datagate.create_item(creatorid=request.session.user.id, parentid=activities.id)
    editor.name = "Question Editor"
    editor.previousid = ''
    editor.view = 'questioneditor'
    editor.save()

    asker = datagate.create_item(creatorid=request.session.user.id, parentid=activities.id)
    asker.name = "Assessment"
    asker.previousid = ''
    asker.view = 'questionasker'
    asker.save()

    findings = datagate.create_item(creatorid=request.session.user.id, parentid=activities.id)
    findings.name = "Findings"
    findings.previousid = ''
    findings.view = 'reportfindings'
    findings.save()

    brainstorming = datagate.create_item(creatorid=request.session.user.id, parentid=activities.id)
    brainstorming.name = "Commenter"
    brainstorming.previousid = ''
    brainstorming.view = 'commenter'
    brainstorming.save()

    groups = meeting.search1(name='groups')
    pm = datagate.create_item(creatorid=request.session.user.id, parentid=groups.id)
    pm.name = "PM"
    pm.sets = ''
    pm.save()
    pmo =  datagate.create_item(creatorid=request.session.user.id, parentid=groups.id)
    pmo.name = "PMO"
    pmo.sets = ''
    pmo.save()
    contractor =  datagate.create_item(creatorid=request.session.user.id, parentid=groups.id)
    contractor.name = "Contractor"
    contractor.sets = ''
    contractor.save()
    stakeholder =  datagate.create_item(creatorid=request.session.user.id, parentid=groups.id)
    stakeholder.name = "Senior Stakeholder"
    stakeholder.sets = ''
    stakeholder.save()
    user =  datagate.create_item(creatorid=request.session.user.id, parentid=groups.id)
    user.name = "User"
    user.sets = ''
    user.save()

    # allow the activity view to initialize itself
    BaseView.views[editor.view.lower()].initialize_activity(request, editor)
    BaseView.views[asker.view.lower()].initialize_activity(request, asker)
    BaseView.views[findings.view.lower()].initialize_activity(request, findings)
    BaseView.views[brainstorming.view.lower()].initialize_activity(request, brainstorming)
    

