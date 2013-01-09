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
import datagate
import threading
import time, traceback
import Events
import GUID
import Directory
import TimedDict


DEFAULT_PROXY_SCRIPT = '''# Example proxy script
# Lines starting with pound are ignored (e.g. for comments)
# All other lines should be in the following format: 
# user_id\tdelay_seconds\tparent_prefix\tcomment
# (the four fields are separated by tabs)
'''

class RatingProxy(BaseView.BaseView):
  NAME = 'Rating Proxy'

  def __init__(self):
    BaseView.BaseView.__init__(self)
    self.sessions = {}
    self.lock = threading.RLock()
    self.scripts = {}
    
      
  def send_content(self, request):
    '''Sends the content pane to the browser'''  
    frame = request.getvalue('_frame', '')
    if frame == 'control':
      self.send_control(request)
      
    else:
      self.send_frames(request)
    
    
  def send_frames(self, request):
    '''Sends the main frames'''
    # start the automatic comments, if needed
    item = datagate.get_item(request.getvalue('global_rootid', ''))
    
    # save rootids
    self.lock.acquire()
    try:
      self.sessions[request.session.id] = item.id
    finally:
      self.lock.release()

    if request.session.user.superuser == '1':
      request.writeln(HTML_HEAD)
      request.writeln("<frameset border='1' cols='40%,*'>")
      request.writeln("<frame marginheight='0' marginwidth='0' name='control' src='" + request.cgi_href(_frame='control') + "'>")
      request.writeln("<frame marginheight='0' marginwidth='0' name='component' src='" + request.cgi_href(view='rating') + "'>")
      request.writeln("</frameset>")
      request.writeln("</html>")   

    else:
      request.writeln(HTML_HEAD)
      request.writeln("<frameset border='0' cols='*'>")
      request.writeln("<frame marginheight='0' marginwidth='0' name='component' src='" + request.cgi_href(view='rating') + "'>")
      request.writeln("</frameset>")
      request.writeln("</html>")   
    
     
  def send_control(self, request):
    '''Sends the control pane'''
    self.lock.acquire()
    try:
      item = datagate.get_item(request.getvalue('global_rootid', ''))
  
      # delete old scripts
      for id in self.scripts.keys():
        if not self.scripts[id].running:
          del self.scripts[id]
  
      request.writeln(HTML_HEAD)
      request.writeln('&nbsp;')
      request.writeln('<p align="center"><b>Proxy Scripting Pane:</b></p>')
      request.writeln('<p align="center"><a href="' + request.cgi_href(script=None, _frame='control') + '">Refresh Window</a></p>')
      request.writeln('<p>&nbsp;</p>')

      request.writeln('Running scripts:')
      request.writeln('<ul>')
      for scriptid, script in self.scripts.items():
        request.writeln('<li>')
        request.writeln(time.strftime('%a, %d %b %Y %H:%M:%S', script.starttime))
        request.writeln('(' + str(script.current) + ' / ' + str(len(script.rows)) + ')')
        request.writeln('[<a href="' + request.cgi_href(gm_action='delscript', scriptid=scriptid, _frame='control') + '">del</a>]')
        request.writeln('</li>')
      request.writeln('</ul>')      
      request.writeln('<p>&nbsp;</p>')
      
      request.writeln('<b>Script:</b><br>')
      request.writeln('[ <a target="systemusers" href="' + request.cgi_href(script=None, view="administrator", adminaction="exportusers", global_adminview=None) + '">Show Users</a> ]<br>')
      request.writeln('<center>')
      request.writeln(request.cgi_form(gm_action='startscript', _script=None, _frame='control'))
      request.writeln('<textarea name=_script cols=60 rows=20>' + DEFAULT_PROXY_SCRIPT + '</textarea>')
      request.writeln('<p><input type=submit value="Start Script"></p>')
      request.writeln('</form>')
      request.writeln('</html>')
    finally:
      self.lock.release()    
    

  def startscript_action(self, request):
    '''starts a new script'''
    script = Script(self, request.getvalue('_script', ''))
    script.start()
    self.scripts[script.id] = script


  def delscript_action(self, request):        
    '''deletes a script'''
    self.scripts[request.getvalue('scriptid', '')].running = 0
        
  
  ################################################
  ###   Administrator functions for the view
    

  def initialize_activity(self, request, root):
    '''Initializes this item'''
    BaseView.get_view('rating').initialize_activity(request, root)
    
    
  def send_admin_page(self, request):
    '''Called from the administrator to allows customization of the activity'''
    BaseView.get_view('rating').send_admin_page(request)

    
    
  ##################################################
  ###   Sends a comment out (from a proxy script)

  def find_parent(self, parent, prefix):
    '''DFS algorithm to find a child.text starting with the given prefix'''
    for child in parent.get_child_items():
      text = child.getvalue('text', '')
      if len(text) >= len(prefix) and text[:len(prefix)] == prefix:
        return child.id
      # check my subchildren
      child = self.find_parent(child, prefix)
      if child: # if we found one, return it
        return child
    return None


  def send_comment(self, userid, prefix, comment):
    self.lock.acquire()  # only send one comment at a time (since we're hitting multiple rootids)
    try:
      sent_to = {}
      for sessionid, rootid in self.sessions.items():
        # get the session; if the session has expired, remove and move on
        session = Directory.get_session(sessionid)
        if not session:
          del self.sessions[sessionid]
          continue
          
        # if we've already sent to this rootid, skip and move on
        if sent_to.has_key(rootid):
          continue
        sent_to[rootid] = rootid
        
        # find the actual parent of this comment
        root = datagate.get_item(rootid)
        if not root:
          print "RatingProxy couldn't find rootid:", rootid
          continue
        parentid = self.find_parent(root, prefix) or rootid
        
        # create and send the event to the system (goes to all interested users)
        # I'm using a blank windowid so it goes to anyone looking at this rootid
        item = datagate.create_item(parentid=parentid, creatorid=userid)
        item.text = comment
        item.save()
        event = BaseView.views['rating']._create_event(item, 'processAdd')
        Events.send_event(rootid, event)
    
    finally:
      self.lock.release()
  
  
  
    
class Script(threading.Thread):
  def __init__(self, rp, script):
    self.running = 1
    self.id = GUID.generate()
    self.ratingproxy = rp
    self.starttime = time.localtime()
    self.rows = script.split("\n")
    threading.Thread.__init__(self)
    self.setDaemon(1)
    self.current = 0
    self.nextsend = 0
    
  def run(self):
    try:
      while self.current < len(self.rows):
        try:
          row = self.rows[self.current].strip()
          self.current += 1
          
          # short circuit if not a line
          if len(row) == 0 or row[0] == '#':
            continue
            
          # split into the four parts
          parts = row.split('\t')
          userid = parts[0]
          delay = parts[1]
          prefix = parts[2]
          comment = '\t'.join(parts[3:])

          # wait the specified amount of time
          while self.nextsend > time.time():
            time.sleep(0.250)  # check every 250 millis
          
          # set up the next sending time (this allows us to send comments without affecting time between comments)
          self.nextsend = time.time() + int(delay)
          
          # if we're not running, stop
          if not self.running:
            return
          
          # send the comment
          self.ratingproxy.send_comment(userid, prefix, comment)    
        except:
          traceback.print_exc()
    except:
      traceback.print_exc()
    self.running = 0