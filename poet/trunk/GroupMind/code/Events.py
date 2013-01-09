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

# Events always happen on children.  They are posted to parent items so the 
# parent view can be notified.
#
# See below for the requirements to create an event from the client-side
# (i.e. form parameters)

import GUID
import datagate
import BaseView
import sys, types, threading
import Constants
from xml.dom import minidom 

###################################################
###   The Event object used for all events

class Event:
  '''This event object is used for all events created by views'''
  def __init__(self, js_handler, *arguments):
    '''Creates an event:
         js_handler = The javascript function on the view to be called.
         arguments  = The arguments to be sent to the function.  This must be a sequence (list or tuple).
    '''
    self.js_handler = js_handler
    self.arguments = arguments


###################################################
###   Event listener map (maps sessions to rootids)

# the common list of event listeners 
# it maps an id to a list of sessions that are interested in it
listener_map = {}
listener_map_lock = threading.RLock()

def add_listener(session, rootid):
  '''Adds a session as a listener to events regarding rootid'''
  listener_map_lock.acquire()
  try:
    Constants.log.debug("Adding session (" + session.user.username + ") as event listener for rootid=" + rootid)
    if listener_map.has_key(rootid):
      sessions = listener_map[rootid]
      if not sessions.has_key(session.id):
        sessions[session.id] = session
    else:
      listener_map[rootid] = { session.id: session }
  finally:
    listener_map_lock.release()
    
    
def remove_session_listeners(sessionid):
  '''Removes all listeners for the given session (called at session cleanup)'''
  # note that the listener_map is optimized for finding by rootid rather than by session
  # since removing a session happens infrequently and events happen all the time
  listener_map_lock.acquire()
  try:
    for rootid, d in listener_map.items():
      if d.has_key(sessionid):
        del d[sessionid]
        if len(d) == 0:
          del listener_map[rootid]
  finally:
    listener_map_lock.release()
    
      
def send_event(rootid, event):
  '''Posts javascript function calls ("events") to all interested windows'''
  if listener_map.has_key(rootid):
    Constants.log.debug("  Sending js to sessions:")
    for session in listener_map[rootid].values():
      Constants.log.debug("    -> " + session.user.username)
      session.process(rootid, event)
  else:
    Constants.log.debug("  No listeners for this windowid.  Skipping event.")



    

#####################################################
###   Main action handler -- all events start here
  
def process_actions(request):
  '''Processes all actions in a request'''
  rootid = request.getvalue('global_rootid', '')
  for action in request.getlist('gm_action'):
    # decode the action -- this uses reflection to call the appropriate action
    try:
      view, funcname = action.split('.')[:2]
    except ValueError: # no period was sent in
      view = request.getvalue('global_view', '')
      funcname = action

    # get a ref to the module and func desired
    try:
      func = getattr(BaseView.views[view.lower()], funcname + '_action')  # I add _action for security reasons.  It ensures that no method except one ending with _action can ever be called from a browser form.
    except KeyError:
      Constants.log.warning('Action error: View (' + str(view) + ') in "' + str(action) + '" not found.  Action aborted.')
      continue
      
    # unwrap the arguments to the function
    args = [ request ]
    i = 1
    while True:
      arg = request.getvalue('gm_arg' + str(i))
      if arg == None:
        break
      args.append(Constants.gm_arg_decode(arg)) # javascript in BaseView explicitly encodes arguments since they have to go into a URL, even for post (that's AJAX rules)
      i += 1
      
    # let the function do its work
    # the function should return a single Event object or a list of Event objects
    events = apply(func, args)

    # send the javascript to windows interested in this rootid
    if events:
      if isinstance(events, Event):
        send_event(rootid, events)
      else:
        for event in events:
          send_event(rootid, event)  
          
         
         
##########################################
###   Sending of events to the client
         
def send_events_xml(request):
  '''Sends any new events that are in this client's event queue.'''
  # get the events
  if request.session:
    events = request.session.get_events(request.getvalue('global_windowid',''), request.getvalue('global_rootid', ''))
    
  else:  # if we don't have a session anymore (meaning it probably timed out), send the XML command to log in again          
    events = [ Event('gm_loginAgain') ]

  # create XML from the events
  doc = minidom.Document()
  root = doc.appendChild(doc.createElement('groupmind'))
  for event in events:
    eventnode = root.appendChild(doc.createElement('event'));
    eventnode.setAttribute('handler', event.js_handler)
    if event.arguments:
      for arg in event.arguments:
        process_argument(arg, doc, eventnode)
      
  # send back to the client
  if len(events) > 0:
    Constants.log.debug("Sending " + str(len(events)) + " events to window " + request.getvalue("global_windowid", ""))

  # send the xml to the client 
  doc.writexml(request.out)
        
      
      
def process_argument(arg, doc, parent):
  '''Puts an argument into the XML.  Recursive so embedded lists can be recursively processed'''
  argnode = parent.appendChild(doc.createElement('argument'));
  if isinstance(arg, (types.ListType, types.TupleType)):
    argnode.setAttribute('type', 'list')
    for item in arg:
      process_argument(item, doc, argnode)
  
  elif isinstance(arg, types.DictType):
    argnode.setAttribute('type', 'dict')
    for key, value in arg.items():
      process_argument(key, doc, argnode)
      process_argument(value, doc, argnode)
  
  else:
    argnode.appendChild(doc.createCDATASection(str(arg)))
    # set the type
    if isinstance(arg, types.BooleanType):
      argnode.setAttribute('type', 'bool')
    elif isinstance(arg, (types.IntType, types.LongType)):
      argnode.setAttribute('type', 'int')
    elif isinstance(arg, types.FloatType):
      argnode.setAttribute('type', 'float')
    else:
      argnode.setAttribute('type', 'string')
