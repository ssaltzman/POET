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

class Login(BaseView):
  NAME = 'Login Pane'

  def __init__(self):
    BaseView.__init__(self)
     
  def send_content(self, request):
    '''Shows the user login page'''
    # get the view
    view = request.getvalue('view', 'meetingchooser').lower()
    if view == 'login' or view == 'logout':
      view = 'meetingchooser'
    
    # see if the user wants to be logged out
    if request.getvalue('action', '') == 'logout' and request.session != None:
      Directory.logout(request.session)
    
    # write the page
    request.writeln(HTML_HEAD_NO_CLOSE + '''
      <script language='JavaScript' type='text/javascript'>
      <!--
        // ensure we are the top-most window (so a hidden frame doesn't go 
        // to a login window that the user can't see)
        // this happens when 
        // 1. the events try to refresh and the session has timed out
        // 2. an error occurs somewhere, the url is broken, and the app resets itself 
        if (top != window) {
          alert("Please login again.\\n\\nYour session has likely timed out.");
          top.location.replace("''' + request.cgi_href(gm_action="logout") + '''");
        }
      -->
      </script>      
      </head>
      
    ''' + HTML_BODY)
    
    request.writeln('''<script src="''' + join(WEB_PROGRAM_URL, 'jquery-1.4.2.min.js') + '''"></script>''')
    request.writeln('''<script src="''' + join(WEB_PROGRAM_URL, 'jquery-ui-1.8.2.custom.min.js') + '''"></script>''')
    request.writeln('''<link href="''' + join(WEB_PROGRAM_URL, 'jquery-ui-1.8.2.custom.css') + '''" rel="stylesheet" type="text/css"/>''')
    
    request.writeln('''
    
      <script type="text/javascript">
	$(function() {
		$("input:submit").button();
	});
      </script>
      
      <div id="login">
        <div id="bigPoetLogo">POET</div>
        <div id="login-input"> 
          ''' + request.cgi_form(view=view, username=None, password=None, global_view='meetingchooser') + '''
            Username:<br/><input type="text" name="username" size="50"><br/><br/>
            Password:<br/><input type="password" name="password" size="50"><br/><br/>
            <input class="submit" type='submit' value="Login">
          </form>
        </div>
        
        <div id="login-info">
          <p>
          Note: This application makes heavy use of <a target="_blank" href="http://www.w3schools.com/dhtml/">DHTML</a> 
          for its dynamic interfaces.  It requires
          a current browser that includes extensive <a target="_blank" href="http://www.w3.org/DOM/">W3C DOM</a> support.  
          It has been tested with the following browser versions:
          </p>
          <ul>
            <li><a target="_blank" href="http://www.microsoft.com/windows/ie/default.asp">Microsoft Internet Explorer</a> Version 6+.</li>
            <li><a target="_blank" href="http://www.mozilla.org/">Mozilla</a> or one of its <a target="_blank" href="http://www.mozilla.org/projects/distros.html">derivatives</a>:
              <ul>
                <li><a target="_blank" href="http://www.mozilla.org/">Firefox</a>: It's a whole new web.</li>
                <li><a target="_blank" href="http://channels.netscape.com/ns/browsers/default.jsp">Netscape Navigator</a> Version 6+.</i>
                <li><a target="_blank" href="http://www.mozilla.org/projects/camino/">Camino</a>: The primary Mozilla-based Mac OS X browser.</li>
                <li><a target="_blank" href="http://galeon.sourceforge.net/">Galeon</a>: A Linux GTK+ Mozilla-based browser.</li>
                <li>Many <a target="_blank" href="http://www.mozilla.org/projects/distros.html">others</a> exist...
              </ul>
            </li>
          </ul>
          <p>
           As of 2004, Safari, Opera, and others are not yet compliant enough to run GroupMind.
           The browser requirement is not a whim of the programmers, but rather a consequence of the
           use of Javascript, CSS, and the DOM.  The functions required
           by the application are simply not available in most other browsers.  We expect this list to grow
           as new versions of other browsers become more DHTML-compliant. 
           </p>
          <p>
          Groupmind is written and maintained by <a href="mailto:conan@warp.byu.edu">Dr. Conan C. Albrecht</a>. 
          It is distributed without warranty.
          </p>
          <div align="right"><i>GroupMind v''' + VERSION + '''</i></div>
        </div>
      
      </body>
      </html>    
    ''')
      

