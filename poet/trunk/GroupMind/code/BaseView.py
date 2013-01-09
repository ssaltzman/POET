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
import Directory
import GUID
import datagate
import Events
from StringIO import StringIO
import time
import os
import os.path

FRAME_CONTENT = 'content'
FRAME_EVENTS = 'events'
MEETING_ROOT_ITEM = 'MeetingRootItem'


# this is the base class of all views
class BaseView:
  rights_list = [ 'View', 'Add', 'Edit', 'Delete' ]

  def __init__(self):
    '''Constructor'''
    # The interactive flag determines whether a view is interactive
    # Non-interactive views (default) just display content.  They do not register for events.  
    # Interactive views are sent the events via AJAX calls.
    # This must be called after the BaseView constructor
    self.interactive = 0 # views are not interactive by default

    # The deep_items flag determines whether a view controls items that are more than one 
    # level deep.  For example, a tree is deep because it manages not only the chidlren of
    # the root item, but also the hierarchical children beneath the each node at each level.
    # Views are not deep by default.  An example of a non-deep view is the Commenter, which simply
    # displays child items of a root node.
    # This flag is actually used in send_base_frames() below
    # Also in get_data_items
    self.deep_items = 0
    


  ############################################################
  ###   Initialization methods (for the view and for items)

    
  def initialize_item(self, request, item):
    '''Called when a new item is created by the event system and the event has an item_initializer parameter.
       This is called when the event parameters send an 'item_initializer' item.'''
    pass
    
    
  def get_initial_events(self, request, rootid):
    '''Retrieves a list of initial javascript calls that should be sent to the client
       when the view first loads.  Typically, this is a series of add_processor
       events.'''
    return []
    
    
  ############################################################
  ###   Administrator methods
    
  def initialize_activity(self, request, activity):
    '''Allows a view to customize a newly-created Activity.  Called from the Administrator when the 
       view is added to a meeting as an activity.'''
    # first step back up to the meeting
    meeting = activity
    while meeting != None and meeting.getvalue('type', '') != MEETING_ROOT_ITEM:
      meeting = meeting.get_parent()
    if meeting:
      groups_item = meeting.search1(name='groups')
      for group in groups_item.get_child_items():
        for right in self.rights_list:
          setattr(activity, 'groupright_' + group.name + '_' + right, '1')
      activity.save()

    
  def send_admin_page(self, request):
    '''Sends an administrator page for this view.'''
    activity = datagate.get_item(request.getvalue('itemid', ''))
    self.send_admin_rights(request, activity)
    

  def send_admin_rights(self, request, activity, meeting=None):
    '''Sends the administrator html to do rights for this view'''
    # get the data items
    if meeting == None:
      meeting = datagate.get_item(request.getvalue('global_meetingid', ''))
    groups_item = meeting.search1(name='groups')
    
    # process actions from last time
    action = request.getvalue('bvaction', '')
    if action == 'grouprights':
      for group in groups_item.get_child_items():
        for right in self.rights_list:
          if request.getvalue('groupright_' + group.name + '_' + right, '') == 'on':
            setattr(activity, 'groupright_' + group.name + '_' + right, '1')
          else:
            setattr(activity, 'groupright_' + group.name + '_' + right, '0')
      activity.save()
    
    # send the html
    kargs = { 'bvaction': 'grouprights', 'itemid':activity.id }
    for group in groups_item.get_child_items():
      for right in self.rights_list:
        kargs['groupright_' + group.name + '_' + right] = None
    request.writeln(request.cgi_form(**kargs))
    request.writeln('<b>Group Rights:</b>')
    request.writeln('<table border="1" cellspacing="0" cellpadding="2">')
    request.writeln('<tr>')
    request.writeln('<th>Group</th>')
    for right in self.rights_list:
      request.writeln('<th>' + right + '</th>')
    request.writeln('</tr>')
    for group in groups_item.get_child_items():
      request.writeln('<tr>')
      request.writeln('<td>' + group.name + '</td>')
      for right in self.rights_list:
        checked = ''
        key = 'groupright_' + group.name + '_' + right
        if hasattr(activity, key) and getattr(activity, key) == '1':
          checked = " checked"
        request.writeln('<td align="center"><input type="checkbox" name="groupright_' + group.name + '_' + right + '"' + checked + '></td>')
      request.writeln('</tr>')
    request.writeln('</table>')
    request.writeln('<input type="submit" value="Save">')
    request.writeln('</form>')


  def get_user_rights(self, request, activity=None):
    '''Returns the current user's rights for the given activity, or None if not found'''
    # is this the superuser?
    rights = {}
    if request.session.user.superuser == '1':
      for right in self.rights_list:
        rights[right] = 1
      return rights

    # compile them up for regular users 
    if activity == None:     
      activity = datagate.get_item(request.getvalue('global_rootid', ''))    
    if hasattr(activity, 'linkitemid'): # the group rights might be stored in a linked item
      activity = datagate.get_item(activity.linkitemid)
    meeting = datagate.get_item(request.getvalue('global_meetingid', ''))
    group = Directory.get_group(meeting.id, request.session.user.id)
    for right in self.rights_list:
      key = 'groupright_' + group.name + '_' + right
      if hasattr(activity, key) and getattr(activity, key) == '1':
        rights[right] = 1
      else:
        rights[right] = 0
    return rights 
      
    
    

    

  ############################################################
  ###   Client view methods
    
  def handle_request(self, request, viewname):
    '''Handles the main request.'''
    # send the common javascript that every view enjoys
    request.writeln('''
      <script language='JavaScript' type='text/javascript'>
        /* Clears an input field (the first time it is entered) */
        function clearField(field) {
          if (!field.cleared) { // only clear once
            field.value = '';
          }
          field.cleared = true;
        }
        
        /* Confirms a url given a message before going to it in a target frame */
        function confirm_target_url(msg, frame, urlst) {
          if (confirm(msg)) {
            frame.location.href = urlst;
          }
        }
        
        /* Confirms a url given a message before going to it */    
        function confirm_url(msg, urlst) {
          confirm_target_url(msg, window, urlst);
        }
        
        /* Retrieves the text children of an XML node */
        function getNodeText(node) {
          var text = "";
          for (var i = 0; i < node.childNodes.length; i++) {
            if (node.childNodes[i].nodeType == 3) { // IE doesn't recognize the TEXT_NODE constant
              text += node.childNodes[i].nodeValue;
            }
          }
          return text;
        }
        
        /* Translates the evt object to get a cross-browser event source element.
           Note that this is a JavaScript event, and it has nothing to do with the
           server-side event system! */
        function getEventSource(evt) {
          // this code is taken from Dynamic HTML Reference by Danny Goodman
          evt = (evt) ? evt : ((event) ? event : null);
          if (evt) {
            var elem = (evt.target) ? evt.target : ((evt.srcElement) ? evt.srcElement : null);
            if (elem) {
              return elem;
            }
          }
          return null;
        }
        
        /* Replaces all occurances of one string within another string (JavaScript's replace only does one - this ensures consistencies across DOM implementations) */
        function replaceAll(st, oldSt, newSt) {
          // short circuit
          if (st == null || oldSt == null || newSt == null) {
            return st;
          }//if
          var buf = "";
          // step through and replace each occurance
          var current = 0;
          var pos;
          while ((pos = st.indexOf(oldSt, current)) >= 0) {
            buf += st.substring(current, pos);
            buf += newSt;
            current = pos + oldSt.length;
          }//while
      
          // add any remaining text at the end
          buf += st.substring(current, st.length);
          return buf;  
        }
         
        /* Convenience method to get the first child with nodeName=name (case insensitive) for an element */
        function xmlGetChild(node, name) {
          for (var i = 0; i < node.childNodes.length; i++) {
            var child = node.childNodes.item(i);
            if (child.nodeName.toLowerCase() == name.toLowerCase()) {
              return child;
            }
          }
        }
        /* Convenience method to get a list of children with nodeName=name (case insensitive) for an element */
        function xmlGetChildren(node, name) {
          var children = new Array();
          for (var i = 0; i < node.childNodes.length; i++) {
            var child = node.childNodes.item(i);
            if (child.nodeName.toLowerCase() == name.toLowerCase()) {
              children[children.length] = child;
            }
          }
          return children;
        }
        /* Convenience function to clear all children of an XML element */
        function xmlClear(node) {
          while (node.firstChild != null) { 
            node.removeChild(node.firstChild);
          }
        }
            
        /*
         * Javascript's native encodeURI and encodeURIComponent does not handle all characters,
         * (and base64 doesn't work either because it uses reserved characters in the url,)
         * so I have a homegrown solution that does everything except the following chars:
         */
        var alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890";
        var qualifier = "_";
        var base = 16;
        var pad = 4;
        function encode(st) {
          var newst = "";
          for (var i = 0; i < st.length; i++) {
            if (alphanumeric.indexOf(st.charAt(i)) >= 0) {
              newst += st.charAt(i);
            }else{
              newst += qualifier;
              var h = st.charCodeAt(i).toString(base);
              for (var j = h.length; j < pad; j++) {
                newst += '0';
              }
              newst += h;
            }
          }
          return newst;
        }
        function html(st) {
           ''' + html_conversions + '''
           return st;
        }
        function decode(st) {
          var newst = "";
          for (var i = 0; i < st.length; i++) {
            if (st.charAt(i) == qualifier && st.length >= i + pad + 1) {
              newst += String.fromCharCode(parseInt(st.substring(i+1,i+pad+1), 16));
              i += pad;
            }else{
              newst += st.charAt(i);
            }
          }
          return newst;
        }      

        </script>
    ''')     

    if self.interactive:
      # register for events on this item
      request.windowid = GUID.generate()
      rootid = request.getvalue('global_rootid', '')
      request.session.add_event_queue(request.windowid, rootid) 
      Events.add_listener(request.session, rootid)
      
      # send the initial events for this view to the event system
      for event in self.get_initial_events(request, rootid):
        request.session.process(rootid, event, request.windowid)
        
      # send the interactive code
      request.writeln('''
        <script language='JavaScript' type='text/javascript'>
          var refreshEnabled = false;
          var timerid = -1;
          var eventsRequest = null;
          
          /** Sends a change action to the server.  This function takes the action_method to be called,
              then a variable number of arguments to be sent to the server as part of the call. */
          function sendEvent(action_method) {
            // short circuit if we're already in a call -- we don't allow two calls at once
            if (eventsRequest != null || !refreshEnabled) {
              return;
            }

            // clear the timer (just in case we were called directly)
            if (timerid) {
              clearTimeout(timerid);
            }

            // create the eventsRequest object
            if (window.XMLHttpRequest) { // Mozilla, Safari,...
              eventsRequest = new XMLHttpRequest();
              if (eventsRequest.overrideMimeType) {
                eventsRequest.overrideMimeType('text/xml');
              }
            }else if (window.ActiveXObject) { // IE
              try {
                eventsRequest = new ActiveXObject("Msxml2.XMLHTTP");
              }catch (e) {
                try {
                  eventsRequest = new ActiveXObject("Microsoft.XMLHTTP");
                }catch (e2) {
                  alert("Your browser does not support AJAX.  Please upgrade your browser to run this application");
                  return;
                }
              }
            }

            // wrap up the arguments
            var args = [];
            var debugargs = [];
      ''')
      for key, value in request.get_global_parameters({'gm_contenttype':'text/xml', 
                                                       'gm_internal_action':'send_events_xml',
                                                       'global_windowid': request.windowid,
                                                      }):
        request.writeln('            args[args.length] = "' + key + '=' + value + '";')
      request.writeln('''
      
            // is there an action to encode with this call?
            if (action_method != null) {
              args[args.length] = "gm_action=" + action_method;
              for (var i = 1; i < sendEvent.arguments.length; i++) {
                var arg = sendEvent.arguments[i];
                args[args.length] = "gm_arg" + i + "=" + event_arg_encode(arg);
                debugargs[debugargs.length] = arg;
              }
            }
            
            // show the event in the debugger, if open
            if (top.showDebugEvent) {
              if (action_method == null) {  // a normal update
                //took this out because it causes too much traffic in the events window
                //top.showDebugEvent("QueuePop", "\xA0", "\xA0", "#99FF99");
              }else{
                top.showDebugEvent("Send", action_method, debugargs, "#99CCFF");
              }
            }
            
            // send the request
            eventsRequest.open('POST', "''' + CGI_PROGRAM_URL + '''", true);
            eventsRequest.onreadystatechange = receiveRefreshResponse;
            eventsRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            eventsRequest.send(args.join('&'));
          }//sendEvent function
          
          /** Recursively encodes an argument, including Array types. */
          function event_arg_encode(arg) {
            if (arg instanceof Array && arg.length) { // regular array/python list
              encodedarg = "a";
              for (var i = 0; i < arg.length; i++) {
                encodedarg += event_arg_encode(arg[i]);
              }
              encodedarg += '-';
              return encodedarg;
            }else if (arg instanceof Array) { // associative array/python dictionary
              encodedarg = "d";
              for (key in arg) {
                encodedarg += event_arg_encode(key) + event_arg_encode(arg[key]);
              }
              encodedarg += '-';
              return encodedarg;
            }else if (typeof arg == 'number') {
              if (arg % 1 == 0) {
                return "i" + encode(arg + "") + '-';
              }else{
                return "f" + encode(arg + "") + '-';
              }
            }else if (typeof arg == 'boolean') {
              return "b" + encode(arg ? 'True' : 'False') + '-';
            }else {
              return "s" + encode(arg + "") + '-';
            }          
          }
          
          /** Automatically called by the XMLHttpRequest object with the refresh response from the server */
          function receiveRefreshResponse() {
            // ensure everything is here and we have a good response (this gets called whenever data comes, so it happens multiple times)
            try {
              if (eventsRequest.readyState != 4 || eventsRequest.status != 200) {
                // don't reset anything -- this method will get called again when status == 200 (i.e. everything's here)
                return;
              }
            }catch (e) {  
              // we have to reset everything or else the pop events call won't work next time
              eventsRequest = null;  // reset for next call
              if (timerid) {
                clearTimeout(timerid);
              }
              timerid = setTimeout('sendEvent(null)', ''' + str(POLLING_TIME_IN_SECONDS * 1000) + ''');
              return;
            }

            try {
              // get the XML and free up the eventsRequest object for another call
              var xmldoc = eventsRequest.responseXML;
  
              // get the xml and call the handler function for each event node
              var events = xmldoc.firstChild.childNodes;
              for (var i = 0; i < events.length; i++ ) {
                var event = events[i];
                if (event.nodeName == 'event') {
                  // get the arguments
                  var args = [];
                  for (var j = 0; j < event.childNodes.length; j++) {
                    args[args.length] = event_arg_decode(event.childNodes[j]);
                  }
                  
                  // show the event in the debugger, if open
                  if (top.showDebugEvent) {
                    top.showDebugEvent("Receive", event.getAttribute('handler'), args, "#CCCC99");
                  }

                  // call the function
                  var handler = window[event.getAttribute('handler')];
                  handler.apply(null, args);
                }
              }

            }finally{
              // reset the eventsRequest and timer for another call
              eventsRequest = null;  // reset for next call
              if (timerid) {
                clearTimeout(timerid);
              }
              timerid = setTimeout('sendEvent(null)', ''' + str(POLLING_TIME_IN_SECONDS * 1000) + ''');
            }
          }//receiveRefreshResponse function


          /** Recursively decodes xml-encoded arguments, including Array types. 
              See Events.process_argument for the creator this xml. */
          function event_arg_decode(argnode) {
            if (argnode.nodeName == 'argument') {
              if (argnode.getAttribute('type') == 'list') {
                var args = [];
                for (var j = 0; j < argnode.childNodes.length; j++) {
                  args[args.length] = event_arg_decode(argnode.childNodes[j]);
                }
                return args;
              
              }else if (argnode.getAttribute('type') == 'dict') {
                var args = new Array();
                for (var j = 0; j < argnode.childNodes.length; j += 2) {
                  args[event_arg_decode(argnode.childNodes[j])] = event_arg_decode(argnode.childNodes[j+1]);
                }
                return args;

              }else{
                var value = argnode.firstChild.nodeValue; // CDATA section
                if (argnode.getAttribute('type') == 'bool') {
                  return (value == 'True');
                }else if (argnode.getAttribute('type') == 'int') {
                  return parseInt(value);
                }else if (argnode.getAttribute('type') == 'float') {
                  return parseFloat(value);
                }else {
                  return value;
                }
              }
            }
          }
          
          
          /** Starts the event loop.  Subclasses must call this when they are finished setting up.
              if we started pulling events before the web page is set up, we might call functions that
              don't exist yet.  Because views might be made up of multiple frames, there is no way
              to automatically know when the page is ready (onLoad doesn't work).  Therefore, 
              subclasses MUST call this method when they are done setting up to start the event loop. */
          function startEventLoop() {
            refreshEnabled = true;
            sendEvent(null);
          }
          
          
          /** Disables the refreshing of events from the server.  Call this when you
              want to stop events from happening, such as when the user is entering
              a comment.  Don't forget to enableRefresh() when done! */
          function disableRefresh() {
            refreshEnabled = false;
            if (timerid) {
              clearTimeout(timerid);
            }
          }
          
          
          /** Enables the refreshing of events */
          function enableRefresh() {
            refreshEnabled = true;
            sendEvent(null);
          }
          
          /** Refreshes the events now */
          function refreshEvents() {
            enableRefresh();
          }
          
          /** Tells the client to log in again */
          function gm_loginAgain() {
            alert('Your session has timed out.  Please log in again.');
            window.location.replace("''' + CGI_PROGRAM_URL + '''");
          }
          
        </script>
      ''')
    
    # let the subclass send it's content
    self.send_content(request)

    
  def send_content(self, request):
    '''Sends the default content pane (subclasses should override this)'''
    request.writeln(HTML_HEAD + '''
      ''' + HTML_BODY + '''
      Content frame template from BaseView.send_content().  Please override the send_content() method in the subclass view.
      </body></html>
    ''')
    
    


# set up the views (global to the app, all requests share the same view objects)
# set up the lists to the top-level and regular components
views = {}
log.debug('Loading views...')
for filename in os.listdir(APP_HOME + '/views/'):
  viewname, type = os.path.splitext(filename)
  if type == '.py' and viewname != '__init__':
    log.debug('  Found ' + viewname)
    mod = getattr(__import__('views.' + viewname), viewname)
    cl = getattr(mod, viewname)
    view = cl()
    view.name = viewname.lower()
    views[view.name] = view

  
  
def get_view(name):
  '''Accessor method to get a view object by its name.  Views are singleton objects --
     there is only one object of each view type for the whole program.
  '''
  name = name.lower()
  if views.has_key(name):
    return views[name]
  return None
