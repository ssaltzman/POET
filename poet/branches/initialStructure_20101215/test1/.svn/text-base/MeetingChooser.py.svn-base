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
import Directory
import datagate

class MeetingChooser(BaseView):
  NAME = 'Meeting Chooser'

  def __init__(self):
      BaseView.__init__(self)
     
  def user_is_pm(self, meeting, user_id):
    '''determines whether a given user is the PM of a given meeting'''
    for child in meeting:
     if child.name == "groups":
       for group in child:
         if group.name == "PM":
           for pm_item in group:
             if pm_item.user_id == user_id:
               return True
           return False #if the user isn't in "PM", we're done
    return False #this should never be executed, but just in case

  def send_content(self, request):
    '''Main loop for this view'''
    # get the meetings this user is in
    if request.session.user.superuser == '1':
      #the superuser gets sent straight to the Administrator page
      #pm_meetings = Directory.get_meetings()
      #meetings = []
      self.forward_to_superuser(request)

    
    else:
      pm_meetings = []
      meetings = []
      for meeting in Directory.get_meetings():               
        if Directory.get_group(meeting.id, request.session.user.id) != None:
          if self.user_is_pm(meeting, request.session.user.id):
            pm_meetings.append(meeting)
          else:
            meetings.append(meeting)
    
      # send to the appropriate page
      if len(meetings)+len(pm_meetings) == 0: #and request.session.user.superuser != '1': #superuser is now redirected before this line
        self.no_meetings(request)
      
      elif len(meetings)+len(pm_meetings) == 1: #and request.session.user.superuser != '1': #superuser is now redirected before this line
        if len(meetings) == 1:
          self.forward_to_meeting(request, meetings[0])
        else:
          #self.forward_to_meeting(request, pm_meetings[0])
	  self.forward_to_pm(request, pm_meetings[0])
      
      else:
        self.show_meetings(request, meetings, pm_meetings)
    
  def no_meetings(self, request):
    '''Shows a "you haven't been invited to any meetings yet" screen'''
    request.writeln(HTML_HEAD + HTML_BODY + '''
      <center>
      You have not been included in any programs yet.  
      Please contact your administrator.
      </center>
      </body></html>
    ''')   

  def forward_to_superuser(self, request):
    '''Automatically forwards the superuser to the Administrator homepage'''        
    url = request.cgi_href(global_view="Administrator", global_adminview="")
    request.writeln(HTML_HEAD_NO_CLOSE)
    request.writeln('<script language="JavaScript" type="text/javascript">')
    request.writeln('  window.location.replace("' + url + '");')
    request.writeln('</script>')
    request.writeln('</head>')
    request.writeln(HTML_BODY)
    #request.writeln('You are being <a href="' + url + '">forwarded</a> automatically.')
    request.writeln('</body></html>')
    
  def forward_to_pm(self, request, meeting):
    '''Automatically forwards the superuser to the Administrator homepage'''        
    url = request.cgi_href(itemid=meeting.id, global_meetingid=meeting.id, global_view='Administrator', global_adminview='POET')
    request.writeln(HTML_HEAD_NO_CLOSE)
    request.writeln('<script language="JavaScript" type="text/javascript">')
    request.writeln('  window.location.replace("' + url + '");')
    request.writeln('</script>')
    request.writeln('</head>')
    request.writeln(HTML_BODY)
    request.writeln('</body></html>')
  
  def forward_to_meeting(self, request, meeting):
    '''Automatically forwards a user to a given meeting'''     
    
    url = request.cgi_href(global_rootid=meeting.id, global_meetingid=meeting.id, global_view=meeting.getvalue('global_view', 'POET'))
    request.writeln(HTML_HEAD_NO_CLOSE)
    request.writeln('<script language="JavaScript" type="text/javascript">')
    request.writeln('  window.location.replace("' + url + '");')
    request.writeln('</script>')
    request.writeln('</head>')
    request.writeln(HTML_BODY)
    #request.writeln('You are being <a href="' + url + '">forwarded</a> automatically.')
    request.writeln('</body></html>')  
  
  def show_meetings(self, request, meetings, pm_meetings):
    '''Shows the choose meeting screen to the user'''

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
    request.writeln('</head>')
    #end of added script
    
    request.writeln(HTML_BODY)
    #added nav
    request.writeln('<div id="menu" ''" style="margin:0;padding:0;">')
    request.writeln('<table cellspacing="0" style="border-bottom:#99ccff 1px dotted;padding:3px;" width=100%><tr>')
    request.writeln('''<td id="menu-logo" align=left valign=top>
      			<div id="poet-logo">POET</a>
                       </td>''')

    request.writeln('<td id="user-menu" align=right valign=top>')
    name = request.session.user.name
    request.writeln('logged in as <strong>'+name.title()+'</strong>') #.title capitalizes the first letter of every word
 
    request.writeln('''<span class="divider">|</span> <a onclick='javascript:openHelp();'>Help</a> <span class="divider">|</span> ''')
    request.writeln('<a href="' + request.cgi_href(global_view='login', _adminaction='logout') + '">Logout</a>')
    
    # title
    request.writeln('</td>')
    request.writeln('</tr></table></div>')
    request.writeln('<p>&nbsp;<p>') 
    #end of added nav


    request.writeln("<h1>Please choose your program:</h1>")
    request.writeln("<ul>")
    meetings.sort(lambda a,b: cmp(a.name, b.name))
    pm_meetings.sort(lambda a,b: cmp(a.name, b.name))
    if len(pm_meetings) > 0:
      request.writeln('<li>PM Programs:<ul>')
      for meeting in pm_meetings:        
        request.write('<li>')
        request.write(' <a target="_top" href="' + request.cgi_href(itemid=meeting.id, global_view='Administrator', global_adminview='POET') + '">')
        request.write(meeting.name)
        request.write('</a>')
        if DEBUG:
          request.write(' &nbsp;&nbsp;&nbsp;<a href="' + request.cgi_href(global_view="Debugger", debugview=meeting.getvalue('view', 'poet'), global_rootid=meeting.id) + '">(debug)</a>')
        request.writeln('</li>')
      request.writeln('</ul></li>')

    if len(meetings) > 0:
      request.writeln('<li>User Programs:<ul>')
      for meeting in meetings:
        request.write('<li>')
        request.write('<a href="' + request.cgi_href(global_view=meeting.getvalue('view', 'poet'), global_rootid=meeting.id) + '">')
        request.write(meeting.name)
        request.write('</a>')
        if DEBUG:
          request.write(' &nbsp;&nbsp;&nbsp;<a href="' + request.cgi_href(global_view="Debugger", debugview=meeting.getvalue('view', 'poet'), global_rootid=meeting.id) + '">(debug)</a>')
        request.writeln('</li>')
      request.writeln('</ul></li>')
    request.writeln('</ul>')
        
    if request.session.user.superuser == '1':
      request.writeln("<p>Administrator Options:")
      request.writeln('<ul>')
      request.writeln("<li><a href='" + request.cgi_href(global_view="Administrator") + "'>GroupMind Administrator</a>")
      
      if DEBUG:
        request.write(' &nbsp;&nbsp;&nbsp;<a href="' + request.cgi_href(global_view="Debugger", debugview="Administrator") + '">(debug)</a>')
      request.writeln("</li>")
      request.writeln("<li><a href='" + request.cgi_href(global_view="Sessions") + "'>View Active Sessions</a></li>")
      request.writeln('</ul>')
      
    request.writeln("</body></html>")
    
    
