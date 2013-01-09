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
import random

class QuestionAsker(BaseView):
  NAME = 'Assessment'

  potentialQuestionList = []

  def __init__(self):
      BaseView.__init__(self)
      self.interactive = True
     
  def send_content(self, request):
    # Sends content of page
    request.writeln(HTML_HEAD_NO_CLOSE + '<link type="text/css" rel="stylesheet" href="' + join(WEB_PROGRAM_URL, "layout.css") + '" /></head>')
    request.writeln('''<body onload='setUser("''' + str(request.session.user.id) + '''")'>''')

    thisPage = Directory.get_meeting(request.getvalue('global_rootid', ''))
    parent_id = thisPage.parentid
    parent = datagate.get_item(parent_id)
    grandparent_id = parent.parentid
    meeting = datagate.get_item(grandparent_id)

    thisPage = Directory.get_meeting(request.getvalue('global_rootid', ''))
    parent = thisPage.get_parent()
    meeting = parent.get_parent()

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

    if meeting.status == 0: #this might need rethinking
      msg = "Thank you for logging in.<br/>No questions have been published yet. Please return later to participate."
    else:
      msg = "Thank you for logging in.<br/>You have answered all of the questions that have been assigned to you. You will be informed when more questions or survey results are released to you."

    request.writeln('''<script src="''' + join(WEB_PROGRAM_URL, 'jquery-1.4.2.min.js') + '''"></script>''')
    request.writeln('''<script src="''' + join(WEB_PROGRAM_URL, 'jquery-ui-1.8.2.custom.min.js') + '''"></script>''')
    request.writeln('''<link href="''' + join(WEB_PROGRAM_URL, 'jquery-ui-1.8.2.custom.css') + '''" rel="stylesheet" type="text/css"/>''')

    request.writeln('''

      <script language='JavaScript' type='text/javascript'>
        $(function() {
		$("#progressbar").progressbar({
			value: progress
		});
	});
	
	$(function() {
		$("input:button, input:submit").button();
	});
      
        var currentQuestion;
        var progress;
	var loggedInUser = "";
	
	function openHelp() {
          window.open("''' + WEB_PROGRAM_URL + '''/Help/", "helpwindow", "dependent,height=800,width=1000,scrollbars,resizable");
          return false;
        }
	
	function openProgInfo() {
	  window.open("''' + WEB_PROGRAM_URL + '''/ProgInfo/", "proginfowindow", "dependent,height=800,width=1000,scrollbars,resizable");
          return false;
        }
	
	function setUser(user){
	  logUser(user);
	  window.open("''' + WEB_PROGRAM_URL + '''/ProgInfo/", "proginfowindow", "dependent,height=800,width=1000,scrollbars,resizable");
	}

        function logUser(user){
          loggedInUser = user;
        }
        
        function populateEnd(message,creator,done) {
          if(loggedInUser == ""){
            logUser("'''+str(request.session.user.id)+'''");
          }
	  if(creator == loggedInUser){
	    document.getElementById('progressbar').style.display = "none";   
	    document.getElementById('quesNum').style.display = "none";
	    //document.getElementById('previewQuestion').innerHTML = "'''+msg+'''";
	    document.getElementById('previewQuestion').innerHTML = message;
	    document.getElementById('previewCommentInput').style.display = "none";
	    document.getElementById('questionInput').style.display = "none";
	    document.getElementById('submitButton').style.display = "none";
	    document.getElementById('resetButton').style.display = "none";
            if(done){
              document.getElementById('doneButton').style.display = "none";
              document.getElementById('backButton').style.display = "none";
            }
            else{
              document.getElementById('doneButton').style.display = "inline-block";
              document.getElementById('backButton').style.display = "inline-block";
            }
	    document.getElementById('naInput').style.display = "none";
	  }
        }
        
        function populateForm(question, preselect, answered, asked, creator, set, done) {
          if(loggedInUser == ""){
            logUser("'''+str(request.session.user.id)+'''");
          }
	  if(String(creator) == String(loggedInUser)){
	    document.getElementById('setAssessment').innerHTML = "- " + set + " Questions";
	    currentQuestion = question;
             
	    document.getElementById('progressbar').style.display = "block";   
	    document.getElementById('quesNum').style.display = "block";
	    //document.getElementById('previewCommentInput').style.display = "block";
	    document.getElementById('questionInput').style.display = "block";
	    document.getElementById('backButton').style.display = "inline-block";
	    document.getElementById('submitButton').style.display = "inline-block";
	    document.getElementById('resetButton').style.display = "inline-block";
	    //document.getElementById('naInput').style.display = "none";
            if (done){
              document.getElementById('doneButton').style.display = "inline-block"; 
            }else{
              document.getElementById('doneButton').style.display = "none";
	    }
	    
	    //populates the questions being asked
	   $("#progressbar").progressbar({value: parseInt(100*(answered+1)/asked, 10)});
	    document.getElementById('quesNum').innerHTML = (answered+1) + " of " + asked;
	    document.getElementById('previewQuestion').innerHTML = question[1];
	    formatChanger(question[2], document.getElementById('questionInput'), question[4], question[5]);
	    if(question[3] == "yes"){
	      document.getElementById('previewCommentInput').style.display = "block";
	      document.getElementById('previewComments').value = "";
	    }else{
	      document.getElementById('previewCommentInput').style.display = "none";
	      document.getElementById('previewComments').value = "";
	    }
	    
	    if(question[7] == "na"){
	      document.getElementById('naInput').style.display = "block";
	      if(preselect == "N/A"){
                document.getElementById('naAnswer').checked = true;
	      }
	      else{
                document.getElementById('naAnswer').checked = false;
              }
	      
	    }
	    else{
	      document.getElementById('naInput').style.display = "none";
	      document.getElementById('naAnswer').checked = false;
	    }

            radioButton = document.getElementById(preselect);
            
	    if (null != radioButton){
              radioButton.checked = true;  
            }
	  }
        }

        function formatChanger(format, area, choices, num){
          //changes the answer options depending on which format the question is
          var type = 1;
          switch(format){
            case "truefalse":
              var trueFalse = '<div id="tfInput" class="radio-group">';
              trueFalse += '<span class="radio-option">';
              trueFalse += '<input id="trueInput" type="radio" name="trueFalseInput" value="true" /> ';
              trueFalse += '<label for="trueInput">True</label></span>  ';
              trueFalse += '<span class="radio-option">';
              trueFalse += '<input id="falseInput" type="radio" name="trueFalseInput" value="false" /> ';
              trueFalse += '<label for="falseInput">False</label></span></div>';
              area.innerHTML = trueFalse;
              break;
            case "multiplechoice":
              var multiplePreview = '<div id="listOptions"></div>';
              area.innerHTML = multiplePreview;
              populateOptions(type, choices, num);
              break;
            case "likert":
              var likert = '<div id="likertInput" class="radio-group">';
              likert += '<table cellpadding="6"><tr align="center">';
              likert += '<td><input id="stdInput" type="radio" name="agreementInput" value="stronglydisagree" /></td>';
              likert += '<td><input id="dInput" type="radio" name="agreementInput" value="disagree" /></td>';
              likert += '<td><input id="swdInput" type="radio" name="agreementInput" value="somewhatdisagree" /></td>';
              likert += '<td><input id="nInput" type="radio" name="agreementInput" value="neither" /></td>';
              likert += '<td><input id="swaInput" type="radio" name="agreementInput" value="somewhatagree" /></td>';  
              likert += '<td><input id="aInput" type="radio" name="agreementInput" value="agree" /></td>';
              likert += '<td><input id="staInput" type="radio" name="agreementInput" value="stronglyagree" /></td>';              
              likert += '</tr><tr>';
              likert += '<td><label for="sdInput">Strongly Disagree</label></td>';
              likert += '<td><label for="dInput">Disagree</label></td>';
              likert += '<td><label for="swdInput">Somewhat Disagree</label></td>';
              likert += '<td><label for="nInput">Neither agree<br/>nor disagree</label></td>';
              likert += '<td><label for="swaInput">Somewhat Agree</label></td>';   
              likert += '<td><label for="aInput">Agree</label></td>';
              likert += '<td><label for="staInput">Strongly Agree</label></td>';  
              likert += '</tr></table></div>';
              area.innerHTML = likert;
              break;
            case "yesno":
              var yesNo = '<div id="ynInput" class="radio-group">';
              yesNo += '<span class="radio-option">';
              yesNo += '<input id="yesInput" type="radio" name="yesNoInput" value="yes" /> ';
              yesNo += '<label for="yesInput">Yes</label></span>  ';
              yesNo += '<span class="radio-option">';
              yesNo += '<input id="noInput" type="radio" name="yesNoInput" value="no" /> ';
              yesNo += '<label for="noInput">No</label></span></div>';
              area.innerHTML = yesNo;;
              break;
            case "topn":
              type = 0;
              var topNPreview = "Please select " + num + " items.<br/>"; 
              topNPreview += '<div id="listOptions"></div>';
              area.innerHTML = topNPreview;
              populateOptions(type, choices, num);
              break;
            default:
          }
        }

        function populateOptions(type, allChoices, num){
          //populate available options for the question
          if(allChoices != null){
            var listOptions = "";
            for(var i=0;i<allChoices.length;i++){
              if(type == '0'){
                listOptions += '<input type="checkbox" name="choiceInput" value="' + allChoices[i] + '" /> ';
              }
              else{
                listOptions += '<input type="radio" name="choiceInput" value="' + allChoices[i] + '" /> ';
              }
              listOptions += allChoices[i];
              listOptions += '<br/>';
            }
            document.getElementById('listOptions').innerHTML = listOptions;
          } 
        }  

        //I probably want to make a generic enableButton(buttonId) function instead
        function disableBack(){
          document.getElementById('backButton').disabled = true;
          document.getElementById('backButton').style.visibility = "hidden";
          document.getElementById('backButton').style.display = "none";
          //document.getElementById('backButton').aria-disabled = true;
          //$("#backButton").removeClass("ui-button-disabled").removeClass("ui-state-disabled");
        }

        function enableBack(){
          document.getElementById('backButton').disabled = false;
          document.getElementById('backButton').style.visibility = "visible";
          document.getElementById('backButton').style.display = "inline";
          //document.getElementById('backButton').aria-disabled = false;
          //$("#backButton").addClass("ui-button-disabled").addClass("ui-state-disabled");
        }

        function enableDone(){
          document.getElementById('doneButton').disabled = false;
          document.getElementById('doneButton').style.visibility = "visible";
          document.getElementById('doneButton').style.display = "inline";
          //document.getElementById('doneButton').aria-disabled = false;
          //$("#doneButton").addClass("ui-button-disabled").addClass("ui-state-disabled");
        }


        function submitClicked(){
          enableBack();
          var answer = "";
          if(currentQuestion[6] == "no" && document.getElementById('previewComments').value == ""){
            alert("Please enter a comment.");
          }
          else{
	    if((document.getElementById('naInput').style.display == "block") && (document.getElementById('naAnswer').checked)){
	      answer = "N/A";
	      if(answer == ""){
		alert("No answer was selected");
	      }
	      else{
		sendEvent('answer_question', currentQuestion[0], answer, document.getElementById('previewComments').value);
	      }      
	    }
	    else{
	      switch(currentQuestion[2]){
		case "truefalse":
		  var radios = document.getElementsByName('trueFalseInput');
		  for (var i=0; i <radios.length; i++) {
		    if (radios[i].checked) {
		      answer = radios[i].value;
		    }
		  }
		 if(answer == ""){
		    alert("No answer was selected");
		  }
		  else{
		    sendEvent('answer_question', currentQuestion[0], answer, document.getElementById('previewComments').value);
		  }
		  break;
		case "multiplechoice":
		  var radios = document.getElementsByName('choiceInput');
		  for (var i=0; i <radios.length; i++) {
		    if (radios[i].checked) {
		      answer = radios[i].value;
		    }
		  }
		  if(answer == ""){
		    alert("No answer was selected");
		  }
		  else{
		    sendEvent('answer_question', currentQuestion[0], answer, document.getElementById('previewComments').value);
		  }
		  break;
		case "likert":
		  var radios = document.getElementsByName('agreementInput');
		  for (var i=0; i <radios.length; i++) {
		    if (radios[i].checked) {
		      answer = radios[i].value;
		    }
		  }
		  if(answer == ""){
		    alert("No answer was selected");
		  }
		  else{
		    sendEvent('answer_question', currentQuestion[0], answer, document.getElementById('previewComments').value);
		  }
		  break;
		case "yesno":
		  var radios = document.getElementsByName('yesNoInput');
		  for (var i=0; i <radios.length; i++) {
		    if (radios[i].checked) {
		      answer = radios[i].value;
		    }
		  }
		  if(answer == ""){
		    alert("No answer was selected");
		  }
		  else{
		    sendEvent('answer_question', currentQuestion[0], answer, document.getElementById('previewComments').value);
		  }
		  break;
		case "topn":
		  var radios = document.getElementsByName('choiceInput');
		  for (var i=0; i <radios.length; i++) {
		    if (radios[i].checked) {
		      answer = radios[i].value;
		      if(answer == ""){
			alert("No answer was selected");
		      }
		      else{
			sendEvent('answer_question', currentQuestion[0], answer, document.getElementById('previewComments').value);
		      }
		    }
		  }
		  break;
		default:
	      }
	    }
          }
        }

        function resetClicked(){
          document.getElementById('previewComments').value = "";
          switch(currentQuestion[2]){
              case "truefalse":
                var radios = document.getElementsByName('trueFalseInput');
                for (var i=0; i <radios.length; i++) {
                  radios[i].checked = false ;
                }
                break;
              case "multiplechoice":
                var radios = document.getElementsByName('choiceInput');
                for (var i=0; i <radios.length; i++) {
                  radios[i].checked = false ;
                }
                break;
              case "likert":
                var radios = document.getElementsByName('agreementInput');
                for (var i=0; i <radios.length; i++) {
                  radios[i].checked = false ;
                }
                break;
              case "yesno":
                var radios = document.getElementsByName('yesNoInput');
                for (var i=0; i <radios.length; i++) {
                  radios[i].checked = false ;
                }
                break;
              case "topn":
                var radios = document.getElementsByName('choiceInput');
                for (var i=0; i <radios.length; i++) {
                  radios[i].checked = false ;
                }
                break;
              default:
            }
        }

        function backClicked(){
          sendEvent('back_clicked')
        }

        function doneClicked(){
          //I'd like to call populateEnd here, but I don't have the 'creator' parameter.
          sendEvent('done_clicked');
        }

      </script>
    ''')

    # HTML for the page #
    request.writeln('''
        <br/>
        <div id="container">
        <div id="program-assessment" class="module">
          <h1>Program Assessment <span id="setAssessment"></span></h1>
	  <div id="assessmentContent">
	    <div id="progressbar">               
	    </div>
	    <div id="quesNum">
	    </div>
	    <div id="content"> 
	      <div id="question-viewer">
		<p class="previewText" id='previewQuestion'></p>
		<div class="previewInput">
		  <div id="questionInput" style="float:left;width:95%;">
		  </div>
		  <div id="naInput" align="left" style="float:right;">
		    <br/><input type="checkbox" value="N/A" id="naAnswer" /><br/>N/A 
                  </div>
		  <div id="previewCommentInput" class="comments" style="display:none;">
		    <h3><label for="previewComments">Comments:</label></h3>
		    <textarea id="previewComments" cols="40" rows="3"></textarea>
		  </div>
		  <div class="bottom-toolbar-ask">
		    <div class="questionButtons">
		      <input type="submit" id='backButton' onclick="backClicked()" value="Back" />
		      <input type="submit" id='submitButton' onclick="submitClicked()" value="Submit" />
		      <input type="submit" id='resetButton' onclick="resetClicked()" value="Reset" />
		      <input type="submit" id='doneButton' onclick="doneClicked()" value="Done" />
                      </a>''')
                      
    # This code properly enables/disables the button, but doesn't affect its visibility. Haven't figured out how to get around that.
    '''
    includeBack = True
    backtrack = request.session.user.backtrack
    try:
      previousQuestion = request.session.user.answeredQuestions[backtrack-1] #previous question's id
    except IndexError:
      includeBack = False #there is no previous question -- do not print "Back" button
    if includeBack:
      request.writeln("""<input type="submit" id='backButton' onclick="backClicked()" value="Back" disabled="false" />""")
    else:
      request.writeln("""<input type="submit" id='backButton' onclick="backClicked()" value="Back" disabled="true" />""")
    '''
    request.writeln('''</div>
		  </div>
		</div>
	      </div><!-- /#question-viewer -->
	    </div><!-- /#content -->
	  </div> <!-- /#assessmentContent -->
        </div><!-- /#program-assessment -->
      </div><!-- /#container -->     
    ''')

    request.writeln("<script language='JavaScript' type='text/javascript'>startEventLoop();</script>")
    
    request.writeln("</body></html>")


  ################################################
  ###   Action methods (called from Javascript)

  def filter_params(self,request, setPicked):
    global potentialQuestionList
    creator = request.session.user
    meeting = Directory.get_meeting(request.getvalue('global_rootid', ''))
    parent = meeting.get_parent()
    meetingRoot = parent.get_parent()
    groups = meetingRoot.search1(name='groups')
    activities = parent.search1(view='questioneditor')
    answered = 0
    asked = 0
    question = ''
    answeredQuestionList = []
    userGroup = ''
    userQues = ''
    qId = ''
    events = []
    end = False

    if not setPicked:
      return ["Thank you for logging in.<br/>You currently have no questions assigned for you to answer. You will be informed when questions or survey results are released to you.", 0, 0, 0]
   
    #find which user group user belongs to
    allGroups = groups.get_child_items(self)
    for group in allGroups:
      allChildren = group.get_child_items(self)
      for child in allChildren:
        if creator.id == child.user_id:
          userGroup = group.name

    #get the number of questions already answered by the user
    userAnswer = activities.search1(name="userAnswers")
    for user in userAnswer:
      if user.name == creator.name:
        userQues = user.get_child_items(self)
        #answered = len(userQues)   
        #get the list of question ids of the questions that have already been answered
        for q in userQues:
          answeredQuestionList.append(q.questionId)

    # this is equivalent to potentialQuestionList = list( set(potentialQuestionList) - set(answeredQuestionList) )
    # I'm not sure which is more efficient or readable, though.
    for q in potentialQuestionList[:]:
      for a in answeredQuestionList:
        if q == a:
          potentialQuestionList.remove(q)
    
    #make list of questions from potentialQuestionList and set selected
    setQuestionList = []
    sets = activities.search1(name="sets")
    for s in sets:
      if s.name in setPicked:
        for qIds in s.get_child_items(self):
          if qIds.name == 'quesId':
            for q in qIds.quesId:
              if(potentialQuestionList.count(q) != 0) and q not in setQuestionList:
                setQuestionList.append(q)

    if creator.initialize:
      creator.sessionQuestionList = setQuestionList[:]
      creator.initialize = False

    #asked = len(setQuestionList) + answered
    answered = len(creator.answeredQuestions) + creator.backtrack #"what number question should I ask now?" e.g. 6 questions answered - backtracked twice = question 4
    asked = len(creator.sessionQuestionList) #"how many questions was the user asked in total?"
    done = len(creator.answeredQuestions) >= len(creator.sessionQuestionList) #"has the user answered every question?"

    preselect = ""

    if answered >= asked :
      end = "You have answered all of your questions.</br>Please log in later to view the results."
    else:
      end = ""
      if creator.backtrack < 0:
        questionId = creator.answeredQuestions[creator.backtrack]
        questionXML = datagate.get_item(questionId)
        answers = questionXML.search1(name="answers")
        question = QuestionAsker.get_question(self,questionId)
        
        #if this user has already answered this question, preselect their answer
        answer = None
        for each in answers:
          if each.who == creator.name:
            answer = each
        #answerDictionary translates answers to radioButton IDs
        answerDictionary = {'stronglydisagree': 'stdInput', 'disagree': 'dInput', 'somewhatdisagree': 'swdInput', 'neither': 'nInput',
                            'stronglyagree': 'staInput', 'agree':'aInput', 'somewhatagree':'swaInput', 'N/A':'N/A'}

        preselect = answerDictionary[answer.answer]
      else:
        question = QuestionAsker.get_question(self,setQuestionList[0])
        preselect = ""
    
    params = [end, question, preselect, answered, asked, setPicked, done]
    return params

  def set_picked(self,request):
    creator = request.session.user
    meeting = Directory.get_meeting(request.getvalue('global_rootid', ''))
    parent = meeting.get_parent()
    meetingRoot = parent.get_parent()
    groups = meetingRoot.search1(name='groups')
    allGroups = groups.get_child_items(self)
    for group in allGroups:
      allChildren = group.get_child_items(self)
      for child in allChildren:
        if creator.id == child.user_id:
          return group.sets
    return []

  def next_question(self,request, creator):
    setPicked = QuestionAsker.set_picked(self,request)
    filterParams = QuestionAsker.filter_params(self,request, setPicked)
    events = []
    if not filterParams[0] == "":
      events.append(Event('populateEnd', filterParams[0], str(creator.id), False))
    else:
      events.append(Event('populateForm', filterParams[1], filterParams[2], filterParams[3], filterParams[4], str(creator.id), filterParams[5], filterParams[6]))
    return events

  def answer_question_action(self, request, id, ans, com):
    creator = request.session.user
    item = datagate.get_item(id)
    answers = item.search1(name="answers")
    #if this user has already answered this question, update it instead of creating it
    answer = None
    for each in answers:
      if each.who == creator.name:
        answer = each
    if not answer:
      answer = datagate.create_item(creatorid=creator.id, parentid=answers.id)
    
    answer.name = 'answer'
    answer.who = creator.name
    answer.when = time.strftime('%a, %d %b %Y %H:%M:%S')
    answer.answer = ans
    answer.comment = com
    answer.save()
    
    meeting = Directory.get_meeting(request.getvalue('global_rootid', ''))
    parent = meeting.get_parent()
    activities = parent.search1(view='questioneditor')
    userAnswer = activities.search1(name="userAnswers")
    userFound = False
    if userAnswer != None:
      for user in userAnswer:
        if user.name == creator.name:
          userFound = True
          answered = None
          for child in user:
            if child.questionId == id:
              answered = child
          if not answered:
            answered = datagate.create_item(creatorid=creator.id, parentid=user.id)
          answered.questionId = id
          answered.answer = ans
          answered.when = time.strftime('%a, %d %b %Y %H:%M:%S')
          answered.save()
    if userFound == False or userAnswer == None:
      userCreated = datagate.create_item(creatorid=creator.id, parentid=userAnswer.id)
      userCreated.name = creator.name
      answered = datagate.create_item(creatorid=creator.id, parentid=userCreated.id)
      answered.questionId = id
      answered.answer = ans
      answered.when = time.strftime('%a, %d %b %Y %H:%M:%S')
      answered.save()

    if id not in creator.answeredQuestions:
      creator.answeredQuestions.append(id)

    #creator.backtrack = 0 #resets the user to their first unanswered question
    if creator.backtrack < 0:
      creator.backtrack += 1 #moves the user forward one question
    creator.save()

    event = QuestionAsker.next_question(self,request,creator)
    return event

  def get_question(self,questionId):
    #question = []
    item = datagate.get_item(questionId)
    options = item.search1(name="options")
    allChoices = options.get_child_items(self)
    allOptions = []
    for choice in allChoices:
      allOptions.append(choice.text)
    question = [item.id, item.text, item.format, item.comment, allOptions, options.num_selections, item.comOpt, item.na]
        
    return question

  def back_clicked_action(self, request):
    aQ = request.session.user.answeredQuestions
    creator = request.session.user
    backtrack = creator.backtrack

    events = []
    if (backtrack * -1) < len(aQ):  #hopefully, this will always be true
      request.session.user.backtrack -= 1
    else:
      events.append(Event('disableBack'))

    request.session.user.save()
    event = QuestionAsker.next_question(self,request,creator)
    events.extend(event)
    
    return events #this was "event" for a while -- did that make a difference?

  def done_clicked_action(self, request):
    creator = request.session.user
    msg = "Your session is complete. You may now log off."
    events = []
    events.append(Event('populateEnd', msg, str(creator.id), True))
    return events

  #######################################
  ###   Window initialization methods

  def get_initial_events(self, request, rootid):
    '''Retrieves a list of initial javascript calls that should be sent to the client
       when the view first loads.  Typically, this is a series of add_processor
       events.'''
    global potentialQuestionList
    creator = request.session.user
    meeting = Directory.get_meeting(request.getvalue('global_rootid', ''))
    parent = meeting.get_parent()
    meetingRoot = parent.get_parent()
    groups = meetingRoot.search1(name='groups')
    activities = parent.search1(view='questioneditor')
    userGroup = ''
        
    #find which user group user belongs to
    allGroups = groups.get_child_items(self)
    for group in allGroups:
      allChildren = group.get_child_items(self)
      for child in allChildren:
        if creator.id == child.user_id:
          userGroup = group.name
          #setPicked = group.sets 
          
    setPicked = QuestionAsker.set_picked(self,request)

    #get the question ids of the questions that have already been answered
    groupMapping = activities.search1(name="groupMapping")

    potentialQuestionList = ''
    for group in groupMapping:
      if group.name == userGroup:
        for child in group.get_child_items(self):
          if child.name == 'quesId':
            potentialQuestionList = child.quesId[:]

    filterParams = QuestionAsker.filter_params(self,request,setPicked)
    events = []

    try:
      if (creator.backtrack * -1) < len(creator.answeredQuestions):
        events.append(Event('enableBack'))
      else:
        events.append(Event('disableBack'))
    except AttributeError:
      creator.backtrack = 0
                    
    if not filterParams[0] == "":
      events.append(Event('populateEnd', filterParams[0],str(creator.id), False))
    else:
      events.append(Event('populateForm', filterParams[1], filterParams[2], filterParams[3], filterParams[4], str(creator.id), filterParams[5], filterParams[6]))
    return events

  def initialize_activity(self, request, new_activity):
    '''Called from the Administrator.  Sets up the activity'''
    BaseView.initialize_activity(self, request, new_activity)

    
    
