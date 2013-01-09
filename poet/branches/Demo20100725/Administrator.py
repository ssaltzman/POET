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
import BaseView
import Directory
import datagate
import string
import random

# I explicitly create these lists using *most* of the lowercase characters.
# but I leave out '1' and 'l', '0' and 'o', and other characters that are easily
# confused with each other.  This is used for password generation.
ASCII_CHARS = 'abcdefghkmnopqrstuwxyz'
DIGIT_CHARS = '2345689'

# The top-level components that can be the root views of meetings
top_level_components = [
  'commenter',
  'meetinghome',
  'poet',
  'strikecom',
  'exampleview',
]

class Navigation:
  def __init__(self, request):
    self.itemid = request.getvalue('itemid', '')
    self.global_adminview = request.getvalue('global_adminview', '')
    self.link = '<a href="' + request.cgi_href(_adminaction=None, itemid=request.getvalue('itemid', None)) + '">' + self.global_adminview + '</a>'
    
  def __eq__(self, other):
    return self.itemid == other.itemid and self.global_adminview == other.global_adminview
    

class Administrator(BaseView.BaseView):  
  NAME = 'Administrator'
  
  def __init__(self):
    BaseView.BaseView.__init__(self)


  def send_content(self, request):
    '''All cgi requests come through here.  This assumes that the headers have been sent
       and the output stream is ready'''
    # first check for the superuser
    """if request.session.user.superuser != '1':
      request.writeln(HTML_HEAD + HTML_BODY)
      request.writeln("Error: You are not the superuser.  Please login again with the superuser username and password.")
      request.writeln("</body></html>")
      return"""
      
    # page header
    request.writeln(HTML_HEAD_NO_CLOSE)
    #added script
    request.writeln('''
      <script language='JavaScript' type='text/javascript'>
      <!--
        function openHelp() {
          window.open("''' + WEB_PROGRAM_URL + '''/Help/", "helpwindow", "dependent,height=400,width=300,scrollbars,resizable");
          return false;
        }
        
        function syncParticipants() {
          if (confirm("Syncronize this program's participants to this activity?")) {
            var activityid = document.getElementById('activityid').value;
            sendEvent('gotoActivity', activityid, "''' + request.session.id + '''");
          }
        }
        
      //-->
      </script>''')
    #end of added script
    request.writeln('</head>')
    request.writeln('<body id="menu" ''" style="margin:0;padding:0;">')
    #added nav
    request.writeln('<table cellspacing="0" style="border-bottom:#99ccff 1px dotted;padding:3px;" width=100%><tr>')
    request.writeln('''<td id="menu-logo">
      			<div id="poet-logo">POET</a>
                       </td>''')

    request.writeln('<td id="user-menu">')
    request.writeln('logged in as <strong>'+request.session.user.name+'</strong>')
  
    #navigation
    global_adminview = request.getvalue('global_adminview', '').lower()
    if BaseView.views.has_key(global_adminview) and request.session.user.superuser == '1':
      request.writeln('<span class="divider">|</span> <a href="' + request.cgi_href(_adminaction=None, global_adminview='') + '">Home</a>')
    request.writeln('''<span class="divider">|</span> <a onclick='javascript:openHelp();'>Help</a> <span class="divider">|</span> ''')
    request.writeln('<a href="' + request.cgi_href(global_view='login', _adminaction='logout') + '">Logout</a>')
    
    # title
    request.writeln('</td>')
    request.writeln('</tr></table>')
    request.writeln('<p>&nbsp;<p>')

    # next check to see which view we are administering
    if BaseView.views.has_key(global_adminview):
      BaseView.views[global_adminview].send_admin_page(request)
    else:
      # no admin view?  go to the administrator home
      self.send_administrator_home(request)
      
    
    
  def send_administrator_home(self, request):  
    # write the page title
    request.writeln('''
      <script language='JavaScript' type='text/javascript'>
      <!--
        var global_meetingid = '';
        var meetingview = '';
        var meetingname = '';
        
        function parseSelectedMeeting() {
          global_meetingid = '';
          meetingview = '';
          meetingname = '';
          var meetingselect = document.getElementById('meetingselect');
          if (meetingselect.selectedIndex >= 0) {
            var meetinginfo = meetingselect.options[meetingselect.selectedIndex].value;
            var meetingar = meetinginfo.split('/');
            global_meetingid = meetingar[0];
            meetingview = meetingar[1];
            meetingname = meetingar[2];
          }
        }
      
        function openMeeting() {
          parseSelectedMeeting();
          if (global_meetingid == '') {
            alert("Please select a program.");
          }else{
            window.location.href="''' + request.cgi_href(global_rootid=None, global_view=None) + '''&global_rootid=" + global_meetingid + "&global_view=" + meetingview;
          }
        }
        
        function editMeeting() {
          parseSelectedMeeting();
          if (global_meetingid == '') {
            alert("Please select a program.");
          }else{
            window.location.href="''' + request.cgi_href(itemid=None, global_meetingid=None, global_adminview=None) + '''&itemid=" + global_meetingid + "&global_meetingid=" + global_meetingid + "&global_adminview=" + meetingview;
          }
        }
        
        function exportMeeting() {
          parseSelectedMeeting();
          if (global_meetingid == '') {
            alert("Please select a program.");
          }else{
            window.location.href="''' + request.cgi_href(global_rootid=None, global_view="Export", gm_contenttype='application/x-gzip', contentdisposition="StrikeComGame.gz") + '''&global_rootid=" + global_meetingid;
          }
        }
        
        function copyMeeting(id) {
          parseSelectedMeeting();
          if (global_meetingid == '') {
            alert("Please select a program.");
          }else{
            var text = prompt('Copy To (enter new program name):', '');
            if (text != null && text != '') {
              text = encode(text);
              window.location.href = "''' + request.cgi_href(global_adminview='MeetingHome', _mhaction='copyitem', _itemname=None, _copyitemid=None) + '''&_copyitemid=" + global_meetingid + "&_itemname=" + text;
            }
          }
        }

        function renameMeeting() {
          parseSelectedMeeting();
          if (global_meetingid == '') {
            alert("Please select a program.");
          }else{
            var text = prompt("New Program Name:");
            if (text != null && text != '') {
              text = encode(text);
              window.location.href = "''' + request.cgi_href(_adminaction='editmeetingname', itemid=None, global_meetingid=None, meetingname=None) + '''&global_meetingid=" + global_meetingid + "&meetingname=" + text;
            }
          }
        }
        
        function deleteMeeting() {
          parseSelectedMeeting();
          if (global_meetingid == '') {
            alert("Please select a program.");
          }else if (confirm("Delete this program and all associated data?")) {
            window.location.href="''' + request.cgi_href(_adminaction='delitem', id=None) + '''&id=" + global_meetingid;
          }
        }
        
        function editUser() {
          var userselect = document.getElementById('userselect');
          var userid = userselect.options[userselect.selectedIndex].value;
          if (userid == '') {
            alert('Please select a user to edit');
          }else{
            window.location.href="''' + request.cgi_href(_adminaction="edituser", userid=None) + '''&userid=" + userid;
          }
        }
        
        function deleteUser() {
          var userselect = document.getElementById('userselect');
          var userid = userselect.options[userselect.selectedIndex].value;
          if (userid == '') {
            alert('Please select a non-administrator user to delete');
          }else{
            if (confirm('Delete this user?')) {
              window.location.href="''' + request.cgi_href(_adminaction="deluser", userid=None) + '''&userid=" + userid;
            }
          }
        }

      //-->
      </script>
      </head>
    ''')
    
    # switch based upon the action
    action = request.getvalue('_adminaction', '')
    if action == 'edituser':
      self.edit_user(request)
    
    elif action == 'deluser':
      self.del_user(request)
      self.main_page(request)
      
    elif action == 'delitem':
      self.del_item(request)
      self.main_page(request)
      
    elif action == 'saveuser':
      self.save_user(request)
      self.main_page(request)
      
    elif action == 'generateusers':
      self.generate_users(request)
      
    elif action == 'dogenerateusers':
      self.do_generate_users(request)
      self.main_page(request)
      
    elif action == 'dodeleteusers':
      self.do_delete_users(request)
      self.main_page(request)
      
    elif action == 'exportusers':
      self.export_users(request)
      
    elif action == 'newmeeting':
      meeting = Directory.create_meeting(request.getvalue('meetingname', ''), request.getvalue('meetingview', ''), request.session.user.id)
      meeting.type = BaseView.MEETING_ROOT_ITEM
      meeting.status = 0
      meeting.save()
      
      groups = datagate.create_item(creatorid=request.session.user.id, parentid=meeting.id)  
      groups.name='groups'
      groups.save()
      # allow the view to initialize itself
      BaseView.views[meeting.view.lower()].initialize_activity(request, meeting)
      self.main_page(request)
            
    elif action == 'editmeetingname':
      meeting = datagate.get_item(request.getvalue('global_meetingid', ''))
      meeting.name = request.getvalue('meetingname')
      meeting.save()
      self.main_page(request)
      
    else:
      self.main_page(request)     

    # page footer
    request.writeln("</body></html>")
    
    
  def main_page(self, request):
    '''Shows the main administrator screen'''
    # main page
    request.writeln('''
      <center>
      <table width="100%" border="0" cellspacing="0" cellpadding="5">
      <tr>
        <td width="50%" valign="top">
    ''')
    self.users_page(request)
    request.writeln('''
        </td>
        <td width="50%" valign="top">''')
    self.meetings_page(request)
    request.writeln('''
        </td>
      </tr>
      </table>
      </center>
    ''')
    
  
  def users_page(self, request):
    '''Shows the users (embedded in the main page table)'''
    # the title
    request.writeln('<center><div class="i">Users:</div></center>')
    
    # current users
    request.writeln('''
      <p align="center">
      <select name="userselect" id="userselect" size="15">
    ''')
    users = Directory.get_users()
    users.sort(lambda a,b: cmp(a.username, b.username))
    for user in users:
      if user.superuser == '1':
        request.writeln('<option value="">' + html(user.name) + '</option>')
      else:
        request.writeln('<option value="' + user.id + '">' + html(user.name) + '</option>')
    request.writeln('''
      </select>
      </p>
      <p align="center">
        <a href="javascript:editUser();">Edit</a>
        |
        <a href="javascript:deleteUser();">Delete</a>
      </p>
      <hr>
      <p align="center">
        <a href="''' + request.cgi_href(_adminaction='edituser') + '''">Add New User</a>
        |
        <a href="''' + request.cgi_href(_adminaction='generateusers') + '''">Autogenerate Users</a>
        |
        <a href="''' + request.cgi_href(_adminaction='exportusers') + '''">Export User Information</a>
      </p>
    ''')
  
  def del_user(self, request):
    '''Sets a user as deleted'''
    user = Directory.get_user(request.getvalue('userid', ''))
    user.active = '0'
    user.save()
  
  
  def edit_user(self, request):
    '''Shows the edit user screen'''
    user = Directory.get_user(request.getvalue('userid', 'New'))
    if user == None:
      user = datagate.Item()  # just create a dummy item
      title = "New User"
      userid = 'New'
    else:
      userid = user.id
      title = "Edit User"

    request.writeln('''
      <center><div class="i">''' + title + ''':</div>
      ''' + request.cgi_form(_adminaction='saveuser', userid=userid, name=None, email=None, username=None, password=None, title=None, office=None, work=None, home=None, mobile=None, fax=None, comments=None) + '''
      <table border=0 cellspacing=5><tr>
        <td>Real Name:</td>
        <td><input type="text" name="name" size="30" value="''' + user.getvalue('name', '') + '''"></td>
      </tr><tr>
        <td>Email:</td>
        <td><input type="text" name="email" size="30" value="''' + user.getvalue('email', '') + '''"></td>
      </tr><tr>
        <td>Username:</td>
        <td><input type="text" name="username" size="30" value="''' + user.getvalue('username', '') + '''"></td>
      </tr><tr>
        <td>Password:</td>
        <td><input type="text" name="password" size="30" value="''' + user.getvalue('password', '') + '''"></td>
      </tr><tr>
        <td>Title:</td>
        <td><input type="text" name="title" size="30" value="''' + user.getvalue('title' ,'') + '''"></td>
      </tr><tr>
        <td>Office:</td>
        <td><input type="text" name="office" size="30" value="''' + user.getvalue('office', '') + '''"></td>
      </tr><tr>
        <td>Work Number:</td>
        <td><input type="text" name="work" size="30" value="''' + user.getvalue('work', '') + '''"></td>
      </tr><tr>
        <td>Home Number:</td>
        <td><input type="text" name="home" size="30" value="''' + user.getvalue('home', '') + '''"></td>
      </tr><tr>
        <td>Mobile Number:</td>
        <td><input type="text" name="mobile" size="30" value="''' + user.getvalue('mobile', '') + '''"></td>
      </tr><tr>
        <td>Fax Number:</td>
        <td><input type="text" name="fax" size="30" value="''' + user.getvalue('fax', '') + '''"></td>
      </tr><tr>
        <td valign="top">Comments:</td>
        <td><textarea name="comments" rows=10 cols=50>''' + user.getvalue('comments', '') + '''</textarea></td>
      </tr></table>
      <input type="submit" value="Submit">
      </form>
    ''')   
    
    
  def save_user(self, request):
    '''Saves (or creates) a user'''
    userid = request.getvalue('userid', 'New')
    if (userid == 'New'):
      user = Directory.create_user(request.session.user.id)
    else:
      user = Directory.get_user(userid)
    for key in Directory.USER_FIELDS:
      setattr(user, key, request.getvalue(key, ''))
    user.save()
    
    
  def generate_users(self, request):
    '''Sends the auto generate page'''
    request.writeln('''
      <center><div class="i">Automatically Generate Users</div>
      <p>
      ''' + request.cgi_form(_adminaction='dogenerateusers', name=None, start=None, end=None, passlength=None) + '''
      <table border=0 cellspacing=5><tr>
        <td>Name Prefix:</td>
        <td><input type="text" name="name" size="20" value="Ex: Alpha" onfocus="clearField(this);"></td>
      </tr><tr>
        <td>Starting Number:</td>
        <td><input type="text" name="start" size="8" value="Ex: 1" onfocus="clearField(this);"></td>
      </tr><tr>
        <td>Ending Number:</td>
        <td><input type="text" name="end" size="8" value="Ex: 20" onfocus="clearField(this);"></td>
      </tr><tr>
        <td>Password Length:</td>
        <td><input type="text" name="passlength" size="8" value="Ex: 5" onfocus="clearField(this);"></td>
      </tr></table>
      <input type="submit" value="Submit">
      </form>
      <p>&nbsp;</p>
      <p>&nbsp;</p>
      <hr>
      <p>&nbsp;</p>
      <script language='JavaScript' type='text/javascript'>
      <!--
        function confirmdelete(button) {
          if (confirm("You are about to delete a range of users.  This is *very* serious.\\n\\nAre you sure you want to continue?")) {
            button.form.submit();
          }
        }
      //-->
      </script>
      ''' + request.cgi_form(_adminaction='dodeleteusers', prefix=None) + '''
      <p>Delete Autogenerated Users:</p>
      Delete all users beginning with:
      <input type=text name="prefix" size="20">
      <p>
      <input type="button" value="Delete" onclick="confirmdelete(this)">
      </form>
      </center>
    ''')
    
    
  def do_generate_users(self, request):
    '''Automatically generates users'''
    try:
      name = request.getvalue('name', '')
      assert name != ''
      start = int(request.getvalue('start', 'error'))
      end = int(request.getvalue('end', 'error'))
      passlen = int(request.getvalue('passlength', 'error'))
    except:
      request.writeln('<p align="center"><font color="red">Error: Some fields were not entered correctly or were blank; autogeneration cancelled.</font></p>')
      return
    rand = random.Random()
    index_len = len(str(end))
    for i in range(start, end + 1):
      user = Directory.create_user(request.session.user.id)
      newname = name
      for j in range(len(str(i)), index_len):  # pad lower numbers with zeros
        newname += '0'
      newname += str(i)
      user.name = newname
      user.email = ''
      user.username = newname
      user.password = ''
      if passlen > 0:
        for i in range(passlen - 1):  # all letters except last char is a number
          user.password += rand.choice(ASCII_CHARS)
        user.password += rand.choice(DIGIT_CHARS)
      user.save()
      
      
  def do_delete_users(self, request):
    '''Delete ranges of autogenerated users'''
    prefix = request.getvalue('prefix', '')
    if len(prefix) == 0:
      return
    for user in Directory.get_users():
      if len(user.name) >= len(prefix) and user.name[:len(prefix)] == prefix:
        user.delete()
    
    
  def _format_csv(self, field):
    '''Formats a value for CSV export'''
    qualifier = '"'
    double_qualifier = '""'
    delimiter = ','
    field = str(field)
    field = field.replace(qualifier, double_qualifier)
    if field.find(delimiter) >= 0:
      field = qualifier + field + qualifier
    return field
    
    
  def export_users(self, request):
    '''Exports the users for import into another application'''
    request.writeln('''
      <div align="center" class="i">Export User Information</div>
      <p>
      Copy and paste the following data into your favorite editor.  Save the file with a ".csv" extension and then
      load into Excel or another application.  Note that this feature is present for researchers running treatments 
      (to print out lists of usernames and passwords to give participants) rather than
      for administrators who want to snoop passwords.
      </p>
    ''')
    request.writeln('<pre><tt>')
    request.writeln('User ID,Username,Password,Real Name,Email')
    for user in Directory.get_users():
      request.writeln('\t'.join([ user.id, self._format_csv(user.username), self._format_csv(user.password), self._format_csv(user.name), self._format_csv(user.email)]))
    request.writeln('</tt></pre>')      
     
    
  def del_item(self, request):
    '''Deletes an item'''
    datagate.del_item(request.getvalue('id', 'Empty'))
    
    
    
  def meetings_page(self, request):
    '''Shows the meetings (embedded in the main page table)'''
    request.writeln('<center><div class="i">Programs:</div></center>')
    
    # current meetings
    request.writeln('''
      <p align="center">
      <select name="meetingselect" id="meetingselect" size="15">
    ''')
    
    meetings = Directory.get_meetings()
    meetings.sort(lambda a,b: cmp(a.name, b.name))
    for meeting in meetings:
      request.writeln('<option selected value="' + meeting.id + '/' + meeting.view + '/' + meeting.name + '">' + meeting.name + '</option>')
    request.writeln('''
      </select>
      </p>
      <p align="center">
        <a href="javascript:openMeeting();">Open</a>
        |
        <a href="javascript:editMeeting();">Edit</a>
        |
        <a href="javascript:exportMeeting();">Export</a>
        |
        <a href="javascript:copyMeeting();">Copy</a>
        |
        <a href="javascript:renameMeeting();">Rename</a>
        |
        <a href="javascript:deleteMeeting();">Delete</a>
      </p>
      <hr>
    ''' + request.cgi_form(_adminaction='newmeeting', meetingname=None, meetingview=None) + '''
      New Program:
      <center>
      <table border=0>
        <tr>
          <td>New Program Name:</td>
          <td><input type="text" name="meetingname" size="20"></td>
        </tr><tr>
          <td>New Program Type:</td>
          <td>
            <select name="meetingview">
    ''')
    for name in top_level_components:
      view = BaseView.views[name]
      request.writeln('<option value="' + name + '">' + html(view.NAME) + '</option>')
    request.writeln('''
            </select>
          </td>
        </tr>
      </table>
      <input type="submit" value="Create New Program">
      </form>
      </center>
      
      <hr>
      
    ''' + request.cgi_multipart_form(global_rootid=Directory.meetings_item.id, global_adminview='MeetingHome', _mhaction='import', importfile=None) + '''
      Import Program: 
      <center>
      <table border=0>
        <tr>
          <td>Import File:</td>
          <td><input type="file" name="subaction"></td>
        </tr>
      </table>
      <input type="submit" value="Import">
      </form>
      </center>

      <hr>
      <p>
      * Notes about Exporting:
      <br>
      &nbsp; 1. Programs are saved in XML format.  Information for all users is included with each export.  The structure can be inferred from the XML (sorry, no explicit DTD or Schema).
      <br>
      &nbsp; 2. Export files are gzipped to reduce bandwidth.  <i>Please save the download with a <b>.gz</b> extension</i>.  Programs such as WinZip (Windows) or gunzip (Mac/Unix/Linux) can read gzipped files.
      </p>
      
      
    ''')
    
    
