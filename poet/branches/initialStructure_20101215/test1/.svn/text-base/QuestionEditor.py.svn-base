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

class QuestionEditor(BaseView):
  NAME = 'Question Editor'

  def __init__(self):
      BaseView.__init__(self)
      self.interactive = True
     
  def send_content(self, request):
    # Sends the main content for this view
    request.writeln(HTML_HEAD_NO_CLOSE + '<link type="text/css" rel="stylesheet" href="' + join(WEB_PROGRAM_URL, "layout.css") + '" /></head>')
    request.writeln(HTML_BODY)
    
    request.writeln('''<script src="''' + join(WEB_PROGRAM_URL, 'jquery-1.4.2.min.js') + '''"></script>''')
    request.writeln('''<script src="''' + join(WEB_PROGRAM_URL, 'jquery-ui-1.8.2.custom.min.js') + '''"></script>''')
    request.writeln('''<link href="''' + join(WEB_PROGRAM_URL, 'jquery-ui-1.8.2.custom.css') + '''" rel="stylesheet" type="text/css"/>''')

    request.writeln('''
      <script language='JavaScript' type='text/javascript'>
      
        $(function() {
		$("input:button, input:submit").button();
	});
        
        function addQuestion() {
          sendEvent('add_question');
        }

        function editQuestion(){ 
          var id = document.getElementById('all_questions').value;
          var checkedCategories = new Array();
          var checkedPoet = new Array();

          if(document.getElementById('pol').checked == true){
            checkedPoet.push(document.getElementById('pol').value);
          }
          if(document.getElementById('opt').checked == true){
            checkedPoet.push(document.getElementById('opt').value);
          }
          if(document.getElementById('econ').checked == true){
            checkedPoet.push(document.getElementById('econ').value);
          }
          if(document.getElementById('tech').checked == true){
            checkedPoet.push(document.getElementById('tech').value);
          }     
          
          if(document.getElementById('commentsYes').checked == true){
            var comment = "yes";
            if(document.getElementById('commentsOpt').checked == true){
              var optional = "yes";
            }else{
              var optional = "no";
            }
          }
          else if(document.getElementById('commentsNo').checked == true){
            var comment = "no";
          }

          var users = new Array();
          var usersSelected = document.getElementsByName('users');
          
          for(var i=0;i<usersSelected.length;i++){
            if(document.getElementById('askUser' + i).checked == true){
              users.push(document.getElementById('askUser' + i).value);
            }
          }

          var sets = new Array();
          for (var i=0; i< document.getElementById('setSelection').options.length; i++) {
            if (document.getElementById('setSelection').options[i].selected) {
              sets.push(document.getElementById('setSelection').options[i].value);
            }
          }
          
          if (id == '') {
          }else{
            document.getElementById(id).innerHTML = document.getElementById('questionTextInput').value;
            if( document.getElementById('formatInput').value == 'topn'){
              sendEvent('edit_question', id, document.getElementById('questionTextInput').value, document.getElementById('descriptionInput').value, users, document.getElementById('formatInput').value, comment, optional, document.getElementById('numselections').value, checkedCategories, checkedPoet, sets);
            }else{
              sendEvent('edit_question', id, document.getElementById('questionTextInput').value, document.getElementById('descriptionInput').value, users, document.getElementById('formatInput').value, comment, optional, 0, checkedCategories, checkedPoet, sets);
            }
          }
        }

        function deleteQuestion() {
          var id = document.getElementById('all_questions').value;
          var select = document.getElementById('all_questions');
          for (var i = 0; i < select.length; i++) {
            if (select.options[i].value == id) {
              select.remove(i);
              sendEvent('mark_delete',id);
              if(select.length > 1){
                select.value = select.options[0].value;
                changeDetail();
              }
              return;
            }
          }
          select.value = options[0].value
        }

        function changeDetail() {
          //populates the question form when a question is selected from list
          var id = document.getElementById('all_questions').value;
          if (id == '') {
          }else{
            sendEvent('change_detail', id);
          }
        }              

        function addToQuestionList(id, text, de){
          if(!de){
            var select = document.getElementById('all_questions');
            var option = document.createElement('option');
            option.value = id;
            option.id = id;
            option.appendChild(document.createTextNode(text));
            select.appendChild(option);
            select.value = option.value;
          }
        }

        function addAllUsers(users){
          document.getElementById('userGroupInput').innerHTML = "";
          if(users.length == 0){
            table.disabled = true;
          }

          for(var i = 0; i < users.length; i++){  
            document.getElementById('userGroupInput').innerHTML += "&nbsp;<input type='checkbox' id='askUser" + i + "' name='users' value='" + users[i] +"' />&nbsp;" + users[i] + "<br/>";
          }
        }
        
        function toggleUsers(checked){
          var allUsers = document.getElementsByName('users');
          for( var i =0; i < allUsers.length; i++){
            document.getElementById('askUser'+i).checked = checked;
          }
        }

        function addSets(sets){
          var select = document.getElementById('setSelection');
          document.getElementById('setSelection').innerHTML = "";
          for (var i = 0; i < sets.length; i++){   
            var option = document.createElement('option');
            option.value = sets[i];
            option.appendChild(document.createTextNode(sets[i]));
            select.appendChild(option);
            select.value = option.value;
          }
        }

        function populateForm(text, descrip, users, ansFormat, comment, comOpt, num, options, tags) {
          //Quesiton Form
          document.getElementById('questionTextInput').value = text;
          document.getElementById('descriptionInput').value = descrip;

          var usersSelected = document.getElementsByName('users');
          for(var i=0;i<usersSelected.length;i++){
            document.getElementById('askUser'+ i).checked = false;
          }

          for(var i =0;i<users.length; i++){
            for(var j =0;j<usersSelected.length; j++){
              if(document.getElementById('askUser' + j).value == users[i]){
                document.getElementById('askUser' + j).checked = true;
              }
            }
          }

          for(var i=0; i< document.getElementById('setSelection').options.length; i++){
            document.getElementById('setSelection').options[i].selected = false;
          }

          for(var t = 0; t < tags.length; t++){
            for(var i=0; i< document.getElementById('setSelection').options.length; i++){
              if(document.getElementById('setSelection').options[i].value == tags[t]){
                document.getElementById('setSelection').options[i].selected = true;
              }
            }
          }

          document.getElementById('formatInput').value = ansFormat;

          //Preview
          document.getElementById('previewQuestion').innerHTML = text;
          formatChanger(ansFormat, document.getElementById('questionInput'));
          if(comment == "yes"){
            document.getElementById('previewCommentInput').style.display = "block";
            document.getElementById('commentsYes').checked = true;
            document.getElementById('commentsOpt').disabled = false;
            document.getElementById('commentsRequired').disabled = false;
            if(comOpt == "yes"){
              document.getElementById('commentsOpt').checked = true;
            }else{
              document.getElementById('commentsRequired').checked = true;
            }
          }else{
            document.getElementById('previewCommentInput').style.display = "none";
            document.getElementById('commentsNo').checked = true;
            document.getElementById('commentsOpt').disabled = true;
            document.getElementById('commentsRequired').disabled = true;
          }
          
          var type = 1;
          if(ansFormat == 'topn'){
            type = 0;
          }  
          populateOptions(type, options, num);
        }

        function populateOptions(type, allChoices, num){
          //populates all the available options for a question
          if(allChoices != ""){
            var listOptions = "";
            var listOptionsEditor = "";
            if(type=='0'){
              var select = document.getElementById('numselections');
              select.innerHTML = "";
            }
            for(var i=0;i<allChoices.length;i++){
              if(type == '0'){
                listOptions += '<input type="checkbox" name="choiceInput" value="' + allChoices[i] + '" /> ';
                var option = document.createElement('option');
                option.value = i+1;
                option.appendChild(document.createTextNode(i+1));
                select.appendChild(option);
              }
              else{
                listOptions += '<input type="radio" name="choiceInput" value="' + allChoices[i] + '" /> ';
              }
              listOptions += allChoices[i];
              listOptions += '<br/>';
              listOptionsEditor += allChoices[i];
              var d = "\'" + allChoices[i] + "\'," + type;
              listOptionsEditor += '&nbsp;<a href="javascript:void(0)" onclick="editOption('+ d + ')" >edit</a>';
              listOptionsEditor += '&nbsp;<a href="javascript:void(0)" onclick="deleteOption(' + d + ')" >delete</a><br/>';
            }
            document.getElementById('listOptions').innerHTML = listOptions;
            document.getElementById('optionEditor').innerHTML = listOptionsEditor;
            if(type=='0'){
              select.value = num;
            }
          } 
        }

        function addOption(type){
          var id = document.getElementById('all_questions').value;
          var optionText = document.getElementById('optionsInput').value;
          document.getElementById('optionsInput').value = "";
          if (id == '') {
          }else if(optionText == ''){
            alert("No option was inputed");
          }else{
            sendEvent('add_option', id, optionText, type);
          }
        }

        function editOption(choice, type){
          var newChoice = prompt('Enter new text for option', choice);
          var id = document.getElementById('all_questions').value;
          if (id == '') {
            alert("Please select a question first.");
          }else{
            if(newChoice != null){
              sendEvent('edit_option', id, choice, newChoice, type);
            }
          } 
        }

        function deleteOption(choice, type){
          var id = document.getElementById('all_questions').value;
          if (id == '') {
            alert("Please select a question first.");
          }else{
            sendEvent('delete_option', id, choice, type);
          }
        }

        function populateCategories(checkedPoet){
          //populates the list of available categories and which ones have been selected

          document.getElementById('po').innerHTML = "";
          document.getElementById('et').innerHTML = "";
          
          document.getElementById('po').innerHTML += '&nbsp;<input type="checkbox" id="pol" name="poet" value="Political" />&nbsp;Political<br/>';
          document.getElementById('po').innerHTML += '&nbsp;<input type="checkbox" id="opt" name="poet" value="Operational" />&nbsp;Operational<br/>';
          document.getElementById('et').innerHTML += '&nbsp;<input type="checkbox" id="econ" name="poet" value="Economic" />&nbsp;Economic<br/>';
          document.getElementById('et').innerHTML += '&nbsp;<input type="checkbox" id="tech" name="poet" value="Technical" />&nbsp;Technical<br/>';
          document.getElementById('pol').checked = false;
          document.getElementById('opt').checked = false;
          document.getElementById('econ').checked = false;
          document.getElementById('tech').checked = false;

          if(checkedPoet != ""){
            for(var m = 0; m < checkedPoet.length; m++){
              if(checkedPoet[m] == 'Political'){
                document.getElementById('pol').checked = true;
              }
              else if(checkedPoet[m] == 'Operational'){
                document.getElementById('opt').checked = true;
              }
              else if(checkedPoet[m] == 'Economic'){
                document.getElementById('econ').checked = true;
              }
              else if(checkedPoet[m] == 'Technical'){
                document.getElementById('tech').checked = true;
              }
            }
          }          
        }

        function addNewSet(){
        var tag = prompt("Add in a new set",'');
        sendEvent('add_set',tag);
        }

        function removeSet(){
          var select = document.getElementById('setSelection');
          var sets = new Array();
          for (var i=0; i< select.options.length; i++) {
            if (select.options[i].selected) {
              sets.push(select.options[i].value);
            }
          }
          if (sets.length > 0) {
            sendEvent('remove_sets', sets);
          }
        }

        function formatChanger(format, area){
          //changes details and preview depending on which format is chosen
          document.getElementById('previewQuestion').innerHTML = document.getElementById('questionTextInput').value;
          if(document.getElementById('commentsYes').checked == true){
            document.getElementById('previewCommentInput').style.display = "block";
          }
          else if(document.getElementById('commentsNo').checked == true){
            document.getElementById('previewCommentInput').style.display = "none";
          }
          switch(format){
            case "truefalse":
              var trueFalse = '<div id="tfInput" class="radio-group">';
              trueFalse += '<span class="radio-option">';
              trueFalse += '<input id="trueInput" type="radio" name="trueFalseInput" value="true" /> ';
              trueFalse += '<label for="trueInput">True</label></span>  ';
              trueFalse += '<span class="radio-option">';
              trueFalse += '<input id="falseInput" type="radio" name="trueFalseInput" value="false" /> ';
              trueFalse += '<label for="falseInput">False</label></span></div>';
              document.getElementById('formatEditor').innerHTML = "";
              area.innerHTML = trueFalse;
              break;
            case "multiplechoice":
              var multiple = '<div id="optionEditor"></div>';
              multiple += '<div id="multipleInput">';
              multiple += '<br/><input type="text" id="optionsInput" />';
              multiple += '&nbsp;<a href="#" onclick="addOption(1)">add new</a></div>';
              multiple += '<div id="optionEditor"></div>';
              document.getElementById('formatEditor').innerHTML = multiple;
              var multiplePreview = '<div id="listOptions"></div>';
              area.innerHTML = multiplePreview; 
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
              document.getElementById('formatEditor').innerHTML = "";
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
              document.getElementById('formatEditor').innerHTML = "";
              area.innerHTML = yesNo;;
              break;
            case "topn":
              var topN = '<label for="numselections">Number of selections (N):</label>';
              topN += '<select id="numselections">';
              topN += '</select>';
              topN += '<div id="optionEditor"></div>';
              topN += '<div id="topNInput">';
              topN += '<br/><input type="text" id="optionsInput" />';
              topN += '&nbsp;<a href="javascript:void(0)" onclick="addOption(0)">add new</a></div>';
              topN += '<div id="optionEditor"></div>';
              document.getElementById('formatEditor').innerHTML = topN;
              var topNPreview = '<div id="listOptions"></div>';
              area.innerHTML = topNPreview;  
              break;
            default:
              document.getElementById('formatEditor').innerHTML = "No format was selected";  
          }
        }

      </script>
    ''')

    # HTML for the page #
    request.writeln('''
      <br/>
      <div id="container">
        <h1>Question Editor</h1>
        <div id="content">
          <table id="question-editor-columns">
            <tr>
            
              <td id="col1">
                <div id="question-list" class="module">
                  <h2>Questions</h2>
                  <div id="questionListContent">
                    <div class="top-toolbar">
                      <input type="button" value="Add New" onclick="addQuestion()" />
                      <input type="button" value="Delete Question" onclick="deleteQuestion()" />
                      <!-- <input type="button" value="Export" onclick="javascript:sendEvent('export')" /> -->
                    </div>
                    <select size="10" id="all_questions" onchange="changeDetail()" style="width:570px;"></select>
                  </div> <!-- /#questionListConent -->
                </div><!-- /#question-list -->
              </td>
              
              <td id="col2" rowspan="2">
                <div id="question-details" >
                  <div class="module">
                    <h2>Details</h2>
                    <div id="questionDetailContent">
                      <div class="top-toolbar">
                        <input type="button" value="Save" onclick="editQuestion();" />
                        <input type="button" value="Reset" onclick="populateForm('','','',0,0, '')"/>
                      </div>
                      <table class="form">
                        <tr>
                          <td class="label">
                            <label for="questionTextInput">Text:</label>
                          </td>
                          <td class="value">
                            <textarea id="questionTextInput" cols="40" rows="3"></textarea>
                          </td>
                        </tr>
                        <tr>
                          <td class="label">
                            <label for="descriptionInput">Description:</label>
                          </td>
                          <td class="value">
                            <textarea id="descriptionInput" cols="40" rows="3"></textarea>
                          </td>
                        </tr>
                        <tr>
                          <td class="label">
                            <label for="poetInput">POET Factor:</label>
                          </td>
                          <td class="value">
                            <div id="poetInput">
                              <table id="category-columns">
                                  <tr>
                                          <td><div id="po"></div></td>
                                          <td><div id="et"></div></td>
                                  </tr>
                              </table>
                            </div>    
                          </td>
                        </tr>
                        <tr>
                          <td class="label">
                            <label for="setInput">Tags/Sets:</label>
                          </td>
                          <td class="value">
                            <div id="setInput">
                              <select id="setSelection" multiple size="6">
                              </select>
                              <a href="javascript:void(0)" onclick="addNewSet()">add set</a>
                              &nbsp;
                              <a href="javascript:void(0)" onclick="removeSet()">delete sets</a>
                            </div>    
                          </td>
                        </tr>
                        <tr>
                          <td class="label">
                            <label for="userGroupInput">User Group:</label>
                            <br/><font size="2" >Select: <a href="javascript:void(0)" onclick="toggleUsers(true)">all</a>&nbsp;<a href="javascript:void(0)" onclick="toggleUsers(false)">none</a></font>
                          </td>
                          <td class="value">
                            <table>
                              <tr>
                                <td><div id="userGroupInput" cellspacing="1"></div></td>
                              </tr>
                            </table>
                          </td>
                        </tr>
                        <tr>
                          <td class="label">
                            Comment:
                          </td>
                          <td class="value">
                            <div id="comments-input" class="radio-group">
                              <span class="radio-option">
                                <input id="commentsYes" type="radio" name="commentsInput" value="yes" onclick="document.getElementById('commentsOpt').disabled = false;document.getElementById('commentsRequired').disabled = false;"/>
                                <label for="commentsYes">yes</label>
                              </span>
                              <span class="radio-option">
                                <input id="commentsNo" type="radio" name="commentsInput" value="no" onclick="document.getElementById('commentsOpt').disabled = true;document.getElementById('commentsRequired').disabled = true;" />
                                <label for="commentsNo">no</label>
                              </span>
                            </div><!-- /#comments-input -->
                            <div id="comments-optional" class="radio-group">
                              <span class="radio-option">
                                <input id="commentsOpt" type="radio" name="commentsOptional" value="optional" disabled="disabled" />
                                <label for="commentsYes">optional</label>
                              </span>
                              <span class="radio-option">
                                <input id="commentsRequired" type="radio" name="commentsOptional" value="required" disabled="disabled" />
                                <label for="commentsRequired">required</label>
                              </span>
                            </div><!-- /#comments-optional -->
                          </td>
                        </tr>
                        <tr>
                          <td class="label">
                            <label for="formatInput">Answer Format:</label>
                          </td>
                          <td class="value">
                            <select id="formatInput" onchange="formatChanger(document.getElementById('formatInput').value, document.getElementById('questionInput'))">
                              <option value="truefalse">True or False</option>
                              <option value="yesno">Yes or No</option>
                              <option value="multiplechoice">Multiple Choice</option>
                              <option selected="yes" value="likert">Likert</option>
                              <option value="topn">Top N</option>
                            </select>
                          </td>
                        </tr>
                        <tr>
                          <td>&nbsp;</td>
                          <td class="value">
                            <div id="formatEditor"></div>
                          </td>
                        </tr>  
                      </table>
                    </div> <!-- /#questionDetailContent -->
                  </div><!-- /.container -->
                </div><!-- /#question-details -->
              </td>
            </tr>
            
            <tr>
              <td id="col3"> 
                <div id="question-preview" class="module">
                  <h2>Preview</h2>
                  <div id="questionPreviewContent">
                    <p class="previewText" id='previewQuestion'></p>
                    <div class="previewInput">
                      <div id="questionInput">
                      </div>
                      <div id="previewCommentInput" class="comments" style="display:none;">
                        <h3><label for="previewComments">Comments:</label></h3>
                        <textarea id="previewComments" cols="40" rows="3"></textarea>
                      </div>
                      <div class="bottom-toolbar">
                          <input type="submit" value="Submit" disabled="disabled" />
                          <input type="submit" value="Reset" disabled="disabled" />
                      </div>
                    </div>
                  </div> <!-- /#questionPreviewContent -->
                </div><!-- /#question-preview -->
              </td>
            </tr>
          </table><!-- /#question-editor-columns -->
        </div><!-- /#content -->
      </div><!-- /#container -->     
    ''')

    request.writeln("<script language='JavaScript' type='text/javascript'>startEventLoop();</script>")
    
    request.writeln("</body></html>")

  ################################################
  ###   Action methods (called from Javascript)

  def add_question_action(self, request):
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    creator = request.session.user
    questions = root.search1(name="questions")
    item = datagate.create_item(creatorid=creator.id, parentid=questions.id)
    item.name = "question"
    item.text = "New Question"
    item.delete = False
    item.descrip = ""
    poet = datagate.create_item(creatorid=creator.id, parentid=item.id)
    poet.name = 'poet'
    poet.save()
    sets = datagate.create_item(creatorid=creator.id, parentid=item.id)
    sets.name = 'sets'
    sets.save()
    tagSets = root.search1(name="sets")
    tags = []
    for tag in tagSets:
        tags.append(tag.name)
    meeting = datagate.get_item(request.getvalue('global_meetingid', ''))
    usergroups = meeting.search1(name='groups')
    groups = datagate.get_child_items(usergroups.id)
    users = []
    for group in groups:
      users.append(group.name)
    item.users = []
    item.format = 'likert'
    item.comment = ""
    item.comOpt = ""
    item.save()
    options = datagate.create_item(creatorid=creator.id, parentid=item.id)
    options.name = 'options'
    options.num_selections = 0
    options.save()
    answers = datagate.create_item(creatorid=creator.id, parentid=item.id)
    answers.name = 'answers'
    answers.save()
    events = []
    events.append(Event('addToQuestionList', item.id, item.text, item.delete))
    events.append(Event('addAllUsers', users))
    events.append(Event('addSets', tags))
    events.append(Event('populateForm', item.text, item.descrip, item.users, item.format, item.comment, item.comOpt, options.num_selections, [], ''))
    return events

  def mark_delete_action(self,request,id):
    item = datagate.get_item(id)
    item.delete = True
    item.save()
    events = []
    return events

  def change_detail_action(self, request, id):
    item = datagate.get_item(id)
    options = item.search1(name="options")
    allChoices = options.get_child_items(self)
    allOptions = []
    for choice in allChoices:
      allOptions.append(choice.text)
    sets = item.search1(name="sets")
    tags = []
    for t in sets.get_child_items(self):
      tags.append(t.name)
    poet = item.search1(name="poet")
    checkedFactor = poet.get_child_items(self)
    checkedPoet = []
    for p in checkedFactor:
      checkedPoet.append(p.name)
    categories = []
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    events = []
    events.append(Event('populateCategories', checkedPoet))
    events.append(Event('populateForm', item.text, item.descrip, item.users, item.format, item.comment, item.comOpt, options.num_selections , allOptions, tags))
    return events

  def add_option_action(self, request, id, option, formatType):
    creator = request.session.user
    item = datagate.get_item(id)
    options = item.search1(name="options")
    choice = datagate.create_item(creatorid=creator.id, parentid=options.id)
    choice.text = option
    choice.save()
    allChoices = options.get_child_items(self)
    allOptions = []
    for choice in allChoices:
      allOptions.append(choice.text)
    return Event('populateOptions', formatType, allOptions)

  def edit_option_action(self, request, id, choice, newChoice, formatType):
    item = datagate.get_item(id)
    options = item.search1(name="options")
    allChoices = options.get_child_items(self)
    allOptions = []
    for c in allChoices:
      if(c.text == choice):
        c.text = newChoice
        c.save()
      allOptions.append(c.text)
    return Event('populateOptions', formatType, allOptions)

  def delete_option_action(self, request, id, choice, formatType):
    item = datagate.get_item(id)
    options = item.search1(name="options")
    allChoices = options.get_child_items(self)
    allOptions = []
    for c in allChoices:
      if(c.text == choice):
        c.delete()
      else:
        allOptions.append(c.text)
    return Event('populateOptions', formatType, allOptions)

  def edit_question_action(self, request, id, text, descrip, users, ansFormat, comment, optional, num, categoryIdList, poetCategoryList, tags):
    creator = request.session.user
    item = datagate.get_item(id)
    item.text = text
    item.descrip = descrip
    poet = item.search1(name="poet")
    allPoet = poet.get_child_items(self)    
    for p in allPoet:
      p.delete()
    for factor in poetCategoryList:
      f = datagate.create_item(creatorid=creator.id, parentid=poet.id)
      f.name = factor
      f.save()
    sets = item.search1(name="sets")
    allSets = sets.get_child_items(self)
    for s in allSets:
      s.delete()
    for tag in tags:
      t = datagate.create_item(creatorid=creator.id, parentid=sets.id)
      t.name = tag
      t.save()
    item.format = ansFormat
    item.users = users
    item.comment = comment
    item.comOpt = optional
    item.save()
    options = item.search1(name="options")
    options.num_selections = num
    options.save()
    allChoices = options.get_child_items(self)
    allOptions = []
    for choice in allChoices:
      allOptions.append(choice.text)
    root = datagate.get_item(request.getvalue('global_rootid', '')) 
    events = []
    events.append(Event('populateCategories', poetCategoryList))
    events.append(Event('populateForm', item.text, item.descrip, item.users, item.format, item.comment, item.comOpt, options.num_selections, allOptions, tags))
    return events

  def export_action(self, request):
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    questions = root.search1(name="questions")
    doc = xml.dom.minidom.Document()
    docRoot = doc.appendChild(doc.createElement("QuestionSystem"))
    questionRoot = questions.export().documentElement
    questionRoot.tagName = 'Questions'
    docRoot.appendChild(questionRoot)
    f = open('qaDoc.xml','w')
    print >>f, doc.toxml()

  def add_set_action(self, request, tag):
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    creator = request.session.user
    sets = root.search1(name="sets")
    s = datagate.create_item(creatorid=creator.id, parentid=sets.id)
    s.name = tag
    s.save()
    allTags = []
    for t in sets:
        allTags.append(t.name)
    events = []
    events.append(Event('addSets', allTags))
    return events    

  def remove_sets_action(self, request, setsToRemove):
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    creator = request.session.user
    sets = root.search1(name="sets")

    meeting = datagate.get_item(request.getvalue('global_meetingid', ''))
    usergroups = meeting.search1(name='groups')
    unremovableSets = []
    for group in usergroups:
      if not group.sets == []: #don't bother iterating if there's nothing to compare it to
        for s in setsToRemove[:]: #the [:] makes a copy of the list, so we can safely delete items without messing up the iteration
          if s in group.sets: #if we find a set has been asked to a group...
            setsToRemove.remove(s) #...don't remove it.
            unremovableSets.append(s) #just for error-announcing
    #SHEP: create an error letting the user know why the unremoveableSets weren't removed
    
    setsThatRemain = []
    for child in sets:
      if child.name in setsToRemove:
        child.delete()
      else:
        setsThatRemain.append(child.name)

    # refresh the page
    sets.save()
    events = []
    events.append(Event('addSets', setsThatRemain))
    return events

  #######################################
  ###   Window initialization methods

  def get_initial_events(self, request, rootid):
    '''Retrieves a list of initial javascript calls that should be sent to the client
       when the view first loads.  Typically, this is a series of add_processor
       events.'''
    root = datagate.get_item(rootid) 
    events = []
    checkedPoet = ""
    events.append(Event('populateCategories', checkedPoet))
    meeting = datagate.get_item(request.getvalue('global_meetingid', ''))
    usergroups = meeting.search1(name='groups')
    groups = datagate.get_child_items(usergroups.id)
    users = []
    for group in groups:
      users.append(group.name)
    tagSets = root.search1(name="sets")
    sets = []
    for tag in tagSets:
        sets.append(tag.name)
    
    # the questions list
    for child in root.search1(name="questions"):
      options = child.search1(name="options")     
      allChoices = options.get_child_items(self)
      allOptions = []
      for choice in allChoices:
        allOptions.append(choice.text)
      allSets = child.search1(name="sets")       
      tags = []
      for t in  allSets.get_child_items(self):
        tags.append(t.name)
      events.append(Event('addToQuestionList', child.id, child.text, child.delete))
      events.append(Event('addAllUsers', users))
      events.append(Event('addSets', sets))
      events.append(Event('populateForm', child.text, child.descrip, child.users, child.format, child.comment, child.comOpt, options.num_selections, allOptions, tags))
    return events  

  def initialize_activity(self, request, new_activity):
    '''Called from the Administrator.  Sets up the activity'''
    BaseView.initialize_activity(self, request, new_activity)
    creator = request.session.user
    questions = datagate.create_item(creatorid=creator.id, parentid=new_activity.id)
    questions.name = 'questions'
    questions.save()
    userAnswer = datagate.create_item(creatorid=creator.id, parentid=new_activity.id)
    userAnswer.name = 'userAnswers'
    userAnswer.save()
    sets = datagate.create_item(creatorid=creator.id, parentid=new_activity.id)
    sets.name = 'sets'
    sets.save()
    allTags = ['Mandatory','Commitment','Trust','Mindset','SA','Resources','Complexity','Agility','Teamwork','Demonstrability']
    for t in allTags:
      tag = datagate.create_item(creatorid=creator.id, parentid=sets.id)
      tag.name = t
      tag.save()
    groupMapping = datagate.create_item(creatorid=creator.id, parentid=new_activity.id)
    groupMapping.name = 'groupMapping'
    groupMapping.save()
    activites = new_activity.get_parent()
    meeting = activites.get_parent()
    groups = meeting.search1(name='groups')
    for group in groups:
      newUserGroup = datagate.create_item(creatorid=creator.id, parentid=groupMapping.id)
      newUserGroup.name = group.name
      newUserGroup.save()

    

    
    
