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
from Events import Event
import sys
import datagate
import xml.dom.minidom
import time
import Directory
import math 
import time
from time import localtime, strftime
from xlwt import Workbook
#from xlrd import open_workbook
#from xlutils.copy import copy
import csv

class ReportFindings(BaseView):
  NAME = 'Report Findings'

  def __init__(self):
      BaseView.__init__(self)
      self.interactive = True
     
  def send_content(self, request):
    # Sends content of page
    request.writeln(HTML_HEAD_NO_CLOSE + '<link type="text/css" rel="stylesheet" href="' + join(WEB_PROGRAM_URL, "layout.css") + '" />')
    
    request.writeln('''
    <script src="''' + join(WEB_PROGRAM_URL, 'jquery-1.4.2.min.js') + '''"></script>
    <script src="''' + join(WEB_PROGRAM_URL, 'jquery.selectlist.js') + '''"></script>
    <script src="''' + join(WEB_PROGRAM_URL, 'jquery.selectlist.min.js') + '''"></script>
    <script src="''' + join(WEB_PROGRAM_URL, 'jquery.selectlist.pack.js') + '''"></script>
    <script src="''' + join(WEB_PROGRAM_URL, 'jquery-ui-1.8.2.custom.min.js') + '''"></script>
    <link href="''' + join(WEB_PROGRAM_URL, 'jquery-ui-1.8.2.custom.css') + '''" rel="stylesheet" type="text/css"/>
    <link href="''' + join(WEB_PROGRAM_URL, 'visualize.css') + '''" rel="stylesheet" type="text/css"/>
    <link href="''' + join(WEB_PROGRAM_URL, 'visualize-dark.css') + '''" rel="stylesheet" type="text/css"/>
    <script src="''' + join(WEB_PROGRAM_URL, 'excanvas.js') + '''"></script>
    <script src="''' + join(WEB_PROGRAM_URL, 'EnhanceJS/enhance.js') + '''"></script>
    <script src="''' + join(WEB_PROGRAM_URL, 'visualize.jQuery.js') + '''"></script>

    <script type="text/javascript">

        $(function() {
		$("input:button, input:submit").button();
		$("select#user-filter").selectList();
		$("select#poet-filter").selectList();
		$("select#set-filter").selectList();
	});
        
        </script>

    </head>''')
    request.writeln('<body onLoad="getFindings();">')
    #request.writeln(HTML_BODY)

    request.writeln('''
      <script language='JavaScript' type='text/javascript'>

        function updateTable(htmlString){
          $("#chartDiv").html(htmlString);
          $('#chartDiv').visualize({
		type: 'bar', 
		width: '900', 
		height:'300',
		barGroupMargin:'15',
		barMargin:'1',
		parseDirection:'y'
	});
        }

        function getFilter(){
          var user_selected = $('select#user-filter').selectList( {instance: true} );
          var user_filter = user_selected.val();

          var poet_selected = $('select#poet-filter').selectList( {instance: true} );
          var poet_filter = poet_selected.val();
          
          var set_selected = $('select#set-filter').selectList( {instance: true} );
          var set_filter = set_selected.val();

          return [user_filter, poet_filter, set_filter];
        }

        function getFindings(){
          filter = getFilter();
          sendEvent('get_findings', filter);
        }

        function viewFindings(checkedCategories){   
          //document.getElementById('content').innerHTML = checkedCategories;
        }

        function openHelp() {
          window.open("''' + WEB_PROGRAM_URL + '''/Help/", "helpwindow", "dependent,height=800,width=1000,scrollbars,resizable");
          return false;
        }
	
	function openProgInfo() {
          window.open("''' + WEB_PROGRAM_URL + '''/ProgInfo/", "proginfowindow", "dependent,height=800,width=1000,scrollbars,resizable");
          return false;
        }

        function exportCSV() {
          filter = [["All"], ["All"], ["All"]];
          sendEvent('exportCSV', filter);
        }

        function exportFilteredCSV() {
          filter = getFilter();
          sendEvent('exportCSV', filter);        
        }

        function redirectCSV(){
          window.open("''' + WEB_PROGRAM_URL + '''/POET.csv");
        }

        function redirectToCSV(name){
          window.open("''' + WEB_PROGRAM_URL + '''/AddPOETChart.bas");
          window.open("''' + WEB_PROGRAM_URL + '''/results.xls");
        }

      </script>
    ''')

    # HTML for page #
    '''determines whether a given user is the PM of a given meeting'''
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
      request.writeln('<table cellspacing="0" style="border-bottom:#99ccff 1px dotted;padding:3px;" width=100%><tr>')
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
      request.writeln('</tr></table>')

    for activity in activities:
      if activity.name == "Question Editor":      
        sets = activity.search1(name="sets")
        break


    request.writeln('''
        <br/>
        <div id="container">
        <div id="reportFindings" class="module">
          <h1 style='float:left;'>Findings</h1><br/><br/><br/>
          <div id="resultControls">
	    <div id="exportButtons">
	      <input class="butControls" type="button" value="Export Results" onclick="javascript:exportFilteredCSV();">
	    </div>
	    <div id="exportFilters">
	      <div id="setFilter" style='float:right;'>Set<br/>
		<select onchange="getFindings()" id="set-filter" multiple>
		  ''')
    for s in sets:
      request.writeln('''<option value="'''+s.name+'''" selected>'''+s.name+'''</option>''')

    request.writeln('''
		</select>
	      </div>
	    
	      <div id="poetFilter" style='float:right;'>POET<br/>
		<select onchange="getFindings()" id="poet-filter" multiple>		  
		  <option value="Political" selected>Political</option>
		  <option value="Operational" selected>Operational</option>
		  <option value="Economic" selected>Economic</option>
		  <option value="Technical" selected>Technical</option>
		</select>
	      </div>
	      
	      <div id="userFilter" style='float:right;'>User Group<br/>
		<select onchange="getFindings()" id="user-filter" multiple>
		  <option value="PM" selected>PM</option>
		  <option value="PMO" selected>PMO</option>
		  <option value="Contractor" selected>Contractor</option>
		  <option value="Senior Stakeholder" selected>Senior Stakeholder</option>
		  <option value="User" selected>User</option>
		</select>
	      </div>
	    
	  </div>
	</div>
          
        <div id="content" style="clear:both;">
          <div id="chartDiv"></div>
        </div><!-- /#content -->
      </div><!-- /#reportFindings -->
      </div><!-- /#container -->     
    ''')

    request.writeln("<script language='JavaScript' type='text/javascript'>startEventLoop();</script>")
    
    request.writeln("</body></html>")

  ################################################
  ###   Action methods (called from Javascript)

  def export(self, doc, root, q):
    # helper function to build correct xml of question
    ques = root.appendChild(doc.createElement('question'))
    ques.setAttribute('id', q.id)
    text = ques.appendChild(doc.createElement('text'))
    text.appendChild(doc.createTextNode(q.text))
    descrip = ques.appendChild(doc.createElement('description'))
    descrip.appendChild(doc.createTextNode(q.descrip))
    ansFormat = ques.appendChild(doc.createElement('format'))
    ansFormat.appendChild(doc.createTextNode(q.format))
    
    users = ques.appendChild(doc.createElement('users'))
    allUsers = ''
    for u in q.users:
      allUsers += `u`
    users.appendChild(doc.createTextNode(allUsers))
    
    comment = ques.appendChild(doc.createElement('comment'))
    comment.appendChild(doc.createTextNode(q.comment))
    comOpt = ques.appendChild(doc.createElement('comOpt'))
    comOpt.appendChild(doc.createTextNode(q.comOpt))
    
    options = q.search1(name="options")
    allOptions = options.get_child_items(self)
    opts = ques.appendChild(doc.createElement('options'))
    opts.setAttribute('id', options.id)
    num = opts.appendChild(doc.createElement('num_selections'))
    num.appendChild(doc.createTextNode(str(options.num_selections)))
    for o in allOptions:
      opt = opts.appendChild(doc.createElement('option'))
      opt.setAttribute('id', o.id)
      text = opt.appendChild(doc.createElement('text'))
      text.appendChild(doc.createTextNode(o.text))
    
    """
    gories = q.search1(name="categories")
    allCs = gories.get_child_items(self)
    cats = ques.appendChild(doc.createElement('categories'))
    cats.setAttribute('id', gories.id)
    for cat in allCs:
      ca = cats.appendChild(doc.createElement('category'))
      ca.setAttribute('id', cat.id)
      ca.appendChild(doc.createTextNode(cat.name))
    """

    poet = q.search1(name="poet")
    allPoet = poet.get_child_items(self)
    poetCts = ques.appendChild(doc.createElement('poet'))
    poetCts.setAttribute('id', poet.id)
    for p in allPoet:
      t = poetCts.appendChild(doc.createElement('factor'))
      t.setAttribute('id', p.id)
      t.appendChild(doc.createTextNode(p.name))

    sets = q.search1(name="sets")
    allSets = sets.get_child_items(self)
    tag = ques.appendChild(doc.createElement('sets'))
    tag.setAttribute('id', sets.id)
    for s in allSets:
      ca = tag.appendChild(doc.createElement('set'))
      ca.setAttribute('id', s.id)
      ca.appendChild(doc.createTextNode(s.name))
    
    answers = q.search1(name="answers")
    allAnswers = answers.get_child_items(self)
    answs = ques.appendChild(doc.createElement('answers'))
    answs.setAttribute('id', answers.id)
    for a in allAnswers:
      answ = answs.appendChild(doc.createElement('answer'))
      answ.setAttribute('id', a.id)
      ans = answ.appendChild(doc.createElement('answer'))
      ans.appendChild(doc.createTextNode(a.answer))
      who = answ.appendChild(doc.createElement('who'))
      who.appendChild(doc.createTextNode(a.who))
      when = answ.appendChild(doc.createElement('when'))
      when.appendChild(doc.createTextNode(a.when))
      comment = answ.appendChild(doc.createElement('comment'))
      comment.appendChild(doc.createTextNode(a.comment))
    return doc
  
  def get_findings_action(self, request, filterChoice):
    #log.info("filterChoice = "+str(filterChoice))
    meeting = Directory.get_meeting(request.getvalue('global_rootid', ''))
    parent = meeting.get_parent()
    activities = parent.search1(view='questioneditor')
    questions = activities.search1(name="questions")
    doc = xml.dom.minidom.Document()
    root = doc.appendChild(doc.createElement("QuestionSystem"))
    meta = root.appendChild(doc.createElement('meta'))
    date = meta.appendChild(doc.createElement('exportdate'))
    date.appendChild(doc.createTextNode(time.strftime('%a, %d %b %Y %H:%M:%S')))
    quesRoot = root.appendChild(doc.createElement('questions'))
    xmlDoc = doc
     
    #log.info("*** START OF REPORT ***")
    #log.info("filterChoice = "+str(filterChoice))

    # Iterate through all questions, filter out the questions that match the categories
    count = 0 #only for debugging (but could be useful later)
    for q in questions:
      #log.info(" --- QUESTION --- ")
      users = q.users
      poet = []
      sets = []
      for qchild in q:
        if qchild.name == "poet":
          for p in qchild:
            poet.append(p.name)
        elif qchild.name == "sets":
          for s in qchild:
            sets.append(s.name)
      #log.info("Users:      "+str(users)+" vs. "+str(filterChoice[0]))
      #log.info("Poet:       "+str(poet)+" vs. "+str(filterChoice[1]))
      #log.info("Sets:       "+str(sets)+" vs. "+str(filterChoice[2]))
      
      #these three checks could be rewritten as three calls to a function that takes two lists and returns True if there is any shared element
      # check users
      if 'All' in filterChoice[0]:
        includeUsers = True
      else:
        includeUsers = False
        for filterUser in filterChoice[0]: 
          if filterUser in users:
            includeUsers = True
            break
          
      # check poet
      if 'All' in filterChoice[1]:
        includePoet = True
      else:
        includePoet = False
        for filterPoet in filterChoice[1]: 
          if filterPoet in poet:
            includePoet = True
            break
          
      # check categories
      if 'All' in filterChoice[2]:
        includeSet = True
      else:
        includeSet = False
        for filterSet in filterChoice[2]: 
          if filterSet in sets:
            includeSet = True
            break

      #If you want to force a question to match every element of a filter, use this logic instead:
      """
      includeUsers = True #bool starts as true instead of false
      for filterUser in filterChoice[0]: 
        if filterUser not in users: #check for "not in" as opposed to "in"
          includeUsers = False
          break
      """

      #log.info(str(includeUsers)+str(includePoet)+str(includeSet))
      if includeUsers and includePoet and includeSet: 
      	xmldoc = ReportFindings.export(self, doc, quesRoot, q)
      	count += 1
              
      #q_count+=1
      #log.info(" ---------------- ")
    #log.info("# of matches: "+str(count))
    #log.info("**** END OF REPORT ****")
    f = open('qaDoc.xml','w')
    print >> f, xmlDoc.toxml()	
    requestedQuestion = []
    events = []
    events.append(Event('viewFindings', xmlDoc.toxml()))
    return events

  def exportCSV_action(self, request, filters):
    meeting = Directory.get_meeting(request.getvalue('global_rootid', ''))
    parent = meeting.get_parent()
    meetingRoot = parent.get_parent()
    questioneditor = parent.search1(view='questioneditor')
    questions = questioneditor.search1(name="questions")
    events = []

    groups = meetingRoot.search1(name='groups')
    groupsList = []
    userDictionary = {}    
    for group in groups:
      groupsList.append(group.name)
      userDictionary[group.name] = []
      for user in group:
        userDictionary[group.name].append(user.user_id)

    group_filter = filters[0]
    poet_filter = filters[1]
    sets_filter = filters[2]

    # Step 1: Create a dictionary with a key for every existing combination of [POET]x[Set]x[Group].
    # Each key's entry will be a list of question ids that belong to that combination.
    # This dictionary acts as a "master list" for ordering purposes. 
    qLists = {}
    for q in questions:
      #Please feel free to change these variable names if you come up with something better
      q_poet = [] #the question's poet factors
      q_poetNode = q.search1(name='poet')
      for q_p in q_poetNode:
        q_poet.append(q_p.name)
      if not q_poet: # if q_poet == []
        q_poet = ["None"] #this is only necessary for POET factors, because a question with no sets/groups can't be asked
      if not "All" in poet_filter: #change this to "elif", and questions without a POET factor will survive the filter anyway
        q_poet = filter(lambda x:x in q_poet, poet_filter)
        
      q_sets = [] #the question's sets
      q_setsNode = q.search1(name='sets')
      for q_set in q_setsNode:
        q_sets.append(q_set.name)      
      if not "All" in sets_filter: #"all" is not in the filter set
        q_sets = filter(lambda x:x in q_sets, sets_filter)

      q_groups = q.users #the queston's groups
      if not "All" in group_filter: #"all" is not in the filter set
        q_groups = filter(lambda x:x in q_groups, group_filter)       

      for qp in q_poet: #for...
        for qs in q_sets: #every...
          for qg in q_groups: #combination:
            try:
              qLists[qp+qs+qg].append(q.id) # add it to the relevant list
            except KeyError: #entry doesn't exist yet
              qLists[qp+qs+qg] = [q.id]
            
    # Step 2: Create a dictionary with a key for every combination of [User] x [POET] x [Set] x [Group].
    # Populate it with each entry a list of ints, with ints corresponding to answers to questions.
    # This is almost exactly what the final CSV will look like.
    answerData = {}
    answerDataAveraged = {}
    questionPOETData = {}
    questionSetData = {}
    poetData = {}
    setData = {}
    t = {'stronglydisagree': 1, 'disagree': 2, 'somewhatdisagree': 3, 'neither': 4, 'somewhatagree': 5, 'agree': 6, 'stronglyagree': 7, 'N/A': 8} #translates answers into numbers

    for q in questions:
      q_poet = [] #the question's poet factors
      q_poetNode = q.search1(name='poet')
      for q_p in q_poetNode:
        q_poet.append(q_p.name)
      if not q_poet: # if q_poet == []
        q_poet = ["None"] #this is only necessary for POET factors, because a question with no sets/groups can't be asked
      if not "All" in poet_filter: #change this to "elif", and questions without a POET factor will survive the filter anyway
        q_poet = filter(lambda x:x in q_poet, poet_filter)
        
      q_sets = [] #the question's sets
      q_setsNode = q.search1(name='sets')
      for q_set in q_setsNode:
        q_sets.append(q_set.name)
      if not "All" in sets_filter: #"all" is not in the filter set
        q_sets = filter(lambda x:x in q_sets, sets_filter)

      q_groups = q.users #the question's groups
      if not "All" in group_filter: #"all" is not in the filter set
        q_groups = filter(lambda x:x in q_groups, group_filter)

      answers = q.search1(name='answers') #all the answers that question has received
      for answer in answers: #for every individual answer...
        user = answer.who #who answered it...
        user_id = answer.creatorid
        for qp in q_poet: #and what...
          for qs in q_sets: #categories it...
            for qg in q_groups: #belongs to:
              if user_id in userDictionary[qg]: #ignore the groups the user doesn't belong to
                index = qLists[qp+qs+qg].index(q.id) #fetch the index from the master list
                entry = user+"|"+qp+"|"+qs+"|"+qg #compose a name with "|" marks for division later
                try:
                  answerData[entry][index] = t[answer.answer] #update the appropriate column of the row
                except KeyError: #that row doesn't exist yet -- so make it
                  answerData[entry] = [0] * len(qLists[qp+qs+qg]) #a zero for every question belonging to the poet/set/group
                  answerData[entry][index] = t[answer.answer]
                entryAvg = qp+"|"+qs+"|"+qg #compose a name with "|" marks for division later
                try:
                  answerDataAveraged[entryAvg][index].append(t[answer.answer]) #update the appropriate column of the row
                except KeyError: #that row doesn't exist yet -- so make it
                  answerDataAveraged[entryAvg] = [ [] for i in range(len(qLists[qp+qs+qg])) ]  #an empty list for every question belonging to the poet/set/group
                  answerDataAveraged[entryAvg][index].append(t[answer.answer]) #update the appropriate column of the row
                qpindex = str(q.id)+"|"+qp
                try:
                  text, data = questionPOETData[qpindex]
                  data.append(t[answer.answer])
                  questionPOETData[qpindex] = (text, data)
                except KeyError:
                  questionPOETData[qpindex] = (q.text, [t[answer.answer]])
                qsindex = str(q.id)+"|"+qs
                try:
                  text, data = questionSetData[qsindex]
                  data.append(t[answer.answer])
                  questionSetData[qsindex] = (text, data)
                except KeyError:
                  questionSetData[qsindex] = (q.text, [t[answer.answer]])  
                pindex = qp + "|" + qg
                try:
                  poetData[pindex].append(t[answer.answer])
                except KeyError:
                  poetData[pindex] = [ t[answer.answer] ]
                sindex = qs + "|" + qg
                try:
                  setData[sindex].append(t[answer.answer])
                except KeyError:
                  setData[sindex] = [ t[answer.answer] ]
                                    
    for key in answerDataAveraged.keys():
      for index in range(0,len(answerDataAveraged[key])):
        responses = answerDataAveraged[key][index]
        if len(responses) == 0:
          answerDataAveraged[key][index] = (0,0) #mean = 0, standard deviation = 0
        else:
          mean = float(sum(responses)) / float(len(responses))
          differences = [math.pow(mean-elem, 2) for elem in responses ]
          stddev = math.sqrt( sum(differences) / float(len(differences)) )
          answerDataAveraged[key][index] = (mean, stddev)                     

    for key in questionPOETData.keys():
      text, allResponses = questionPOETData[key]
      if len(allResponses) == 0:
        questionPOETData[key] = (text, 0, 0, 0, [])
      else:
        allResponses.sort()
        responses = filter((lambda x: x < 8), allResponses)
        mean = float(sum(responses)) / float(len(responses))
        differences = [math.pow(mean-elem, 2) for elem in responses ]
        stddev = math.sqrt(sum(differences) / float(len(differences)))
        keySplit = key.split('|')
        qid = keySplit[0]
        questionPOETData[key] = (text, mean, stddev, len(allResponses), allResponses)

    for key in questionSetData.keys():
      text, allResponses = questionSetData[key]
      if len(allResponses) == 0:
        questionSetData[key] = (text, 0, 0, 0, [])
      else:
        allResponses.sort()
        responses = filter((lambda x: x < 8), allResponses)
        mean = float(sum(responses)) / float(len(responses))
        differences = [math.pow(mean-elem, 2) for elem in responses ]
        stddev = math.sqrt(sum(differences) / float(len(differences)))
        keySplit = key.split('|')
        qid = keySplit[0]
        questionSetData[key] = (text, mean, stddev, len(allResponses), allResponses)


    # Step 3: Create the CSV file.
    # Each key of the dictionary created in Step 3 will be transformed into a row of the CSV.
    csv = "Username, POET Factor, Set, Group\n" #the header
    for key in answerData.keys(): #each of these will be a row in the final file
      keySplit = key.split('|') #"Alan|Political|Mandatory|PM" -> ["Alan", "Political", "Mandatory", "PM"]
      string = "{user}, {poet}, {set}, {group}".format(
        user=keySplit[0], poet=keySplit[1], set=keySplit[2], group=keySplit[3]) #the key becomes the first four entries of the row
      for answer in answerData[key]:
        if answer == 8: #user answered N/A
          string += ", NA" #is this the best way to handle this? will non-numerical data create problems later? 
        elif answer > 0:
          string += ", "+str(answer) #if the user answered, add that answer to the end of the row
        else:
          string += ",  " #if the user didn't answer, leave that slot blank
      string += "\n" #move to next row
      csv += string #add to CSV

    book = Workbook()
    #rb = open_workbook('../webroot/GroupMind/results.xls')
    #book = copy(rb)

    #for factor in ["Political", "Operational", "Economical", "Technical"]:
    factors = set([])
    for key in poetData.keys():
      factors.add( key.split('|')[0] )
    for factor in factors:
      date = strftime("%m/%d/%Y", localtime())
      time = strftime("%H:%M:%S", localtime())
      tempCSV = "POET results, "+str(date)+", "+str(time)+"\n\n"
      tempCSV += factor+"\n,Group,Mean,Std Dev\n"
      allData = []
      for group in groupsList: #["PM", "PMO", "Contractor", "Senior Stakeholder", "User"]:
        try:
          responses = poetData[factor+"|"+group]
          responses = filter((lambda x: x < 8), responses)
          allData.extend(responses[:])
          mean = float(sum(responses))/float(len(responses))
          differences = [math.pow(mean-elem, 2) for elem in responses ]
          stddev = math.sqrt(sum(differences) / float(len(differences)))
          tempCSV += ","+group+","+str(mean)+","+str(stddev)+"\n"
        except KeyError:
          tempCSV += ","+group+",0,0\n"
        except ZeroDivisionError:
          tempCSV += ","+group+",0,0\n"
          
      responses = allData
      if len(allData) > 0:
        mean = float(sum(responses))/float(len(responses))
        differences = [math.pow(mean-elem, 2) for elem in responses ]
        stddev = math.sqrt(sum(differences) / float(len(differences)))
        tempCSV += ",Total,"+str(mean)+","+str(stddev)+"\n\n"
      else:
        tempCSV += ",Total,0,0\n\n"
      tempCSV += ",Question ID,Question Text,Mean,Std Dev, Responders, Responses\n"
      for key in questionPOETData.keys():
        qid, qfactor = key.split("|")
        if qfactor == factor:
          datum = questionPOETData[key]
          tempCSV += ',{theqid},"{text}",{mean},{stddev},{responders}'.format(
            theqid=qid, text=datum[0], mean=datum[1], stddev=datum[2], responders=datum[3])
          for answer in datum[4]:
            tempCSV+= ','+str(answer)
          tempCSV += "\n"
          #tempCSV += ','+str(qid)+',"'+text+'",'+str(mean)
      log.info(tempCSV)
      f = open(factor+".csv", 'w')
      print >> f, tempCSV
      f.close()

      ReportFindings.writeExcelSheet(self, book, f.name, factor)

    #for set in ["Mandatory", "Agility", "Trust", etc.]:
    sets = set([])
    
    for key in setData.keys():
      sets.add( key.split('|')[0] )
    sets = list(sets)
    htmlData = []
    firstRow = [""]
    firstRow.extend(groupsList) #["", "PM", "PMO", "Contractor", "Senior Stakeholder", "User"]
    htmlData.append(firstRow) #[ ["", "PM", "PMO", "Contractor", "Senior Stakeholder", "User"] ]
    
    for aset in sets:
      nextRow = [aset] # e.g. ["Mandatory"]
      date = strftime("%m/%d/%Y", localtime())
      time = strftime("%H:%M:%S", localtime())
      tempCSV = "POET results, "+str(date)+", "+str(time)+"\n\n"
      tempCSV += aset+"\n,Group,Mean,Std Dev\n"
      allData = []
      for group in groupsList: #["PM", "PMO", "Contractor", "Senior Stakeholder", "User"]:
        try:
          responses = setData[aset+"|"+group]
          responses = filter((lambda x: x < 8), responses)
          allData.extend(responses[:])
          mean = float(sum(responses))/float(len(responses))
          differences = [math.pow(mean-elem, 2) for elem in responses ]
          stddev = math.sqrt(sum(differences) / float(len(differences)))
          tempCSV += ","+group+","+str(mean)+","+str(stddev)+"\n"
          nextRow.append(mean)
        except KeyError:
          tempCSV += ","+group+",0,0\n"
          nextRow.append(0)
        except ZeroDivisionError:
          tempCSV += ","+group+",0,0\n"
          nextRow.append(0)
      htmlData.append(nextRow)
      
      responses = allData
      if len(allData) > 0:
        mean = float(sum(responses))/float(len(responses))
        differences = [math.pow(mean-elem, 2) for elem in responses ]
        stddev = math.sqrt(sum(differences) / float(len(differences)))
        tempCSV += ",Total,"+str(mean)+","+str(stddev)+"\n\n"
      else:
        tempCSV += ",Total,0,0\n\n"
      tempCSV += ",Question,Text,Mean,Std Dev, Responders, Responses\n"
      for key in questionSetData.keys():
        qid, qset = key.split("|")
        if qset == aset:
          datum = questionSetData[key]
          tempCSV += ',{theqid},"{text}",{mean},{stddev},{responders}'.format(
            theqid=qid, text=datum[0], mean=datum[1], stddev=datum[2], responders=datum[3])
          for answer in datum[4]:
            if answer == 8:
              tempCSV += ',N/A'
            else:
              tempCSV+= ','+str(answer)
          tempCSV += "\n"
          #tempCSV += ','+str(qid)+',"'+text+'",'+str(mean)
      log.info(tempCSV)
      f = open("../webroot/GroupMind/"+aset+".csv", 'w')
      print >> f, tempCSV
      f.close()

      ReportFindings.writeExcelSheet(self, book, f.name, aset)
      
      events.append(Event('redirectToCSV', aset))
    log.info("htmlData: "+str(htmlData))
    #log.info("csv:\n"+csv) #debug
                  
    #f = open('../webroot/GroupMind/POET.csv','w')
    #print >> f, csv

    htmlString = ReportFindings.makeHTMLString(self, htmlData)
    log.info("htmlString = "+htmlString)
    #events.append(Event('redirectCSV'))
    events.append(Event('updateTable', htmlString))
    return events

  def makeHTMLString(self, htmlData):
    htmlString = "<table style=\"display:none;\"><caption>"
    htmlString += "Survey Results" #this could be dynamic
    htmlString += "</caption><thead><tr>"
    htmlString += "<td></td>"
    for header in htmlData[0][1:]: #first row, all items but the first
      htmlString += "<th>"+header+"</th>"
    htmlString += "</tr></thead><tbody>"
    for row in htmlData[1:]: #all rows but the first row
      htmlString += "<tr>"
      htmlString += "<th scope='row'>"+row[0]+"</th>"
      for datum in row[1:]: #current row, all items but the first
        htmlString += "<td>"+str(datum)+"</td>"
      htmlString += "</tr>"
    htmlString += "</tbody></table>"
    return htmlString
      

  def writeExcelRow(self, worksheet, lno, columns):
    cno = 0
    for column in columns:
      try:
        worksheet.write(lno, cno, float(column))
      except ValueError:
        worksheet.write(lno, cno, column)
      cno = cno + 1

  def writeExcelSheet(self, book, csvfile, aset):
     csvreader = csv.reader(open(csvfile, 'rb'))
     sheet = book.add_sheet(aset)
     lno = 0
     for row in csvreader:
       ReportFindings.writeExcelRow(self, sheet, lno, row)
       lno = lno + 1
     book.save('../webroot/GroupMind/results.xls')

  #######################################
  ###   Window initialization methods

  def get_initial_events(self, request, rootid):
    '''Retrieves a list of initial javascript calls that should be sent to the client
       when the view first loads.  Typically, this is a series of add_processor
       events.'''
    meeting = Directory.get_meeting(request.getvalue('global_rootid', ''))
    parent = meeting.get_parent()
    activities = parent.search1(view='questioneditor')
    events = []
    allQuestions = []
    for child in activities.search1(name="questions"):
      item = datagate.get_item(child.id)
      options = item.search1(name="options")
      allChoices = options.get_child_items(self)
      allOptions = []
      for choice in allChoices:
        allOptions.append(choice.text)
      allQuestions.append([child.id, child.text, child.format, child.comment, allOptions, options.num_selections, child.comOpt])
    return events

  def initialize_activity(self, request, new_activity):
    '''Called from the Administrator.  Sets up the activity'''
    BaseView.initialize_activity(self, request, new_activity)

    
    
