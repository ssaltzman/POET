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



class ExampleView(BaseView):
  NAME = 'Example View'
  
  def __init__(self):
    BaseView.__init__(self)
    
    # The interactive flag determines whether a view is interactive
    # Non-interactive views (default) just display content.  They do not register for events.  
    # Interactive views are sent the events via AJAX calls.
    # This must be called after the BaseView constructor.
    self.interactive = True
    
     
  def send_content(self, request):
    request.writeln(HTML_HEAD)
    request.writeln(HTML_BODY)
    
    # Header
    request.writeln('''
      <p>Welcome to the example view.  This view shows programmers how to program a simple,
      interactive view.  Please note the following:
      <ul>
        <li>See the views/ExampleView.py file for programming information on this view.
        <li>If you don't see the colored event log in a separate frame, you are not
            running in debug mode.  Turn on DEBUG=True in the Constants.py file to 
            see debugging information.
      </ul>
      </p>
    ''')
    
    # Example 1
    request.writeln('''
      <h2>Example 1: Simple Alert Box</h2>
      <p>Enter a value, then click the "Show Alert" button.  GroupMind will send the call
      to the server, then back to ALL clients connected.  This example might seem 
      useless, but it shows the most simple client-server-client interaction.  Try opening
      two browsers to this same meeting and you'll see how the event is sent to both
      browsers (the second browser will show the event after the event refresh time
      specified in Constants.py).</p>
      <script language='JavaScript' type='text/javascript'>
        // Notice how the event system automatically unwraps the event to give the appropriate
        // parameters to the method
        function showalert(textToShow) {
          alert(textToShow);
        }
      </script>    
      <!-- Notice that you don't have to use form elements because the sendEvent() method
           is called from Javascript. -->
      <input type="text" id="alerttext" size="40">
      <input type="button" value="Show Alert" onclick="sendEvent('alertbox', document.getElementById('alerttext').value)">
    ''')
    
    # Example 2
    request.writeln('''
      <h2>Example 2: Shared Text</h2>
      <p>The following text is shared by all people connected to the application.  Notice that
         the value you enter here is saved in the data tree so it survives program restarts.
         After setting some text, close your browser and reopen this meeting -- the value 
         will still be there.  Then try restarting the entire server -- again, the value
         will still be there.  Next, open multiple browsers to see how the text changes on 
         both browsers.</p>
      <script language='JavaScript' type='text/javascript'>
        /** Sends the text to the server */
        function sendSharedText() {
          sendEvent('change_sharedtext', document.getElementById('sharedtextinput').value);
          document.getElementById('sharedtextinput').value = "";
        }
        /** Receives the text back from the server */
        function receiveSharedText(text) {
          var span = document.getElementById('sharedtext');
          span.firstChild.nodeValue = text;
        }
      </script>    
      <p>Shared text is currently: <span id="sharedtext">Nothing yet.</span></p>
      Change the text: <input type="text" id="sharedtextinput" size="40">
      <input type="button" value="Change Text" onclick="sendSharedText()">
    ''')
    
    # Example 3
    request.writeln('''
      <h2>Example 3: Shared List Box</h2>
      <p>The following list box is shared by by all people connected to the application.
         This example shows how to use child elements in the data tree.</p>
      <script language='JavaScript' type='text/javascript'>
        /** Sends a list item to the server */
        function sendListItem() {
          sendEvent('add_listitem', document.getElementById('listitemtext').value);
          document.getElementById('listitemtext').value = "";
        }
        /** Delets a list item from the server */
        function deleteListItem() {
          var id = document.getElementById('lister').value;
          if (id == '') {
            alert("Please select an item first.");
          }else{
            sendEvent('delete_listitem', id);
          }
        }
        /** Receives a list itme back from the server */
        function receiveListItem(id, text) {
          // modifying the html page inline here (these are normal xml methods, which are quite cross platform)
          var select = document.getElementById('lister');
          var option = document.createElement('option');
          option.value = id;
          option.appendChild(document.createTextNode(text));
          select.appendChild(option);
        }
        /** Receives a delete event from the server */
        function receiveDeleteItem(id) {
          var select = document.getElementById('lister');
          for (var i = 0; i < select.length; i++) {
            if (select.options[i].value == id) {
              select.remove(i);
              return;
            }
          }
        }
      </script>    
      <p>List is:<br><select size="10" id="lister"></select>
      <input type="button" value="Delete Item" onclick="deleteListItem()">
      </p>
      <p>Add an item: <input type="text" id="listitemtext" size="40">
      <input type="button" value="Add List Item" onclick="sendListItem()">
      </p>
    ''')

    # Example 4
    request.writeln('''
      <h2>Example 4: Form action</h2>
      <p>The following form will add an item to the above list box, but it does so through a 
         regular form tag.  It shows how to use a form instead of the sendEvent method.  Obviously,
         this method doesn't use AJAX -- it refreshes the window.  However, this type of action
         can be useful when using frames (see the Commenter.py add and edit panes or when using
         non-interactive screens (see the Administrator).</p>
      ''' + request.cgi_form(gm_action='add_listitem2') + '''
      <p>Add an item: <input type="text" name="listitemtext2" size="40">
      <input type="submit" value="Add List Item">
      </p>
      </form>
    ''')
    
    # Example 5
    request.writeln('''
      <h2>Example 5: Lists in events</h2>
      <p>The following example shows how lists can be 
         sent in events from the server to client.  Javascript Array objects
         can be sent from the client to server.  Javascript Arrays always
         convert to and from Python lists.</p>
      <p>Type text into one box and click the arrow.  The program splits the 
         text into a Javascript Array (by hard returns), then sends to the
         server.  It then returns the list to the client, and turns the Rrray
         back into text for the other text box.</p>
      <script language='JavaScript' type='text/javascript'>
        /** Sends text to the server in a list */
        function sendTextarea(source, dest) {
          var text = document.getElementById(source).value;
          var ar = text.split('\\n');
          sendEvent('send_text_area', dest, ar);
        }
        /** Receives a list itme back from the server */
        function receiveTextArea(dest, ar) {
          var st = ar.join('\\n');
          document.getElementById(dest).value = st;
        }
      </script>    
      <table border=0 cellspacing=15 cellpadding=0>
        <tr>
          <td>
            <textarea id="text1" rows="10" cols="20">111
222
333
444</textarea>
          </td><td>
            <input type="button" value="->" onclick="sendTextarea('text1', 'text2')">
            <br>&nbsp;<br>
            <input type="button" value="<-" onclick="sendTextarea('text2', 'text1')">
          </td><td>
            <textarea id="text2" rows="10" cols="20"></textarea>
          </td>
        </tr>
      </table>

    ''')

    # Example 6
    request.writeln('''
      <h2>Example 6: Variable types</h2>
      <p>One of the most difficult parts of web programming is dealing with string
         POSTs and returns.  What if you want to pass an integer, list, dictionary, or boolean
         to your action?  GroupMind automatically converts the strings on each side
         for you.  The following buttons send different variable types to the server. On the
         server side, they are converted to the appropriate Python type, and on the
         return to the Javascript client, they are again converted to the appropriate
         type.  The type is printed to the console from the server.  As of now,
         these are the only types that can be sent between server and client.
         Anything else is defaulted to a string.</p>
      <script language='JavaScript' type='text/javascript'>
        /** Sends a variable to the server */
        function sendType(v) {
          sendEvent('send_var_type', v);
        }
        function prettyprint_arguments(args) {
          if (args instanceof Array && args.length) {
            var formatted = [];
            for (var i = 0; i < args.length; i++) {
              formatted[i] = prettyprint_arguments(args[i]);
            }
            return '[' + formatted.join(', ') + ']';
          }else if (args instanceof Array) {
            var formatted = [];
            for (key in args) {
              formatted[formatted.length] = prettyprint_arguments(key) + ":" + prettyprint_arguments(args[key]);
            }
            return '{' + formatted.join(', ') + '}';
          }else{
            return args;
          }
        }
        /** Receives a variable back from the server */
        function receiveType(v) {
          if (v instanceof Array && v.length) {
            alert("Normal Array: " + prettyprint_arguments(v));
          }else if (v instanceof Array) {
            alert("Associative Array: " + prettyprint_arguments(v));
          }else if (typeof v == 'number') {
            alert("Number: " + v + " (JS doesn't specifically differentiate integers and floats)");
          }else if (typeof v == 'boolean') {
            alert("Boolean: " + v);
          }else{
            alert("String: " + v);
          }
        }
        var assocarray = [];
        assocarray['hi'] = 'there';
        assocarray['go'] = 'home';
      </script>    
      <div align="center"><input type="button" value="Send String" onclick="sendType('MyStringValue')"></div>
      <div align="center"><input type="button" value="Send Integer" onclick="sendType(1024)"></div>
      <div align="center"><input type="button" value="Send Float" onclick="sendType(3.14)"></div>
      <div align="center"><input type="button" value="Send Boolean" onclick="sendType(true)"></div>
      <div align="center"><input type="button" value="Send JS Array/Python List" onclick="sendType([1,2,'hi',['inner', 'array'],5])"></div>
      <div align="center"><input type="button" value="Send JS Assoc. Array/Python Dictionary" onclick="sendType(assocarray)"></div>
    ''')
    
    # this MUST be called to start the page's event system
    request.writeln("<script language='JavaScript' type='text/javascript'>startEventLoop();</script>")

    # end the page
    request.writeln("</body></html>")
    
    
    
  ################################################
  ###   Action methods (called from Javascript)
  
  # Notice on this action method (called from sendEvent() in the javascript above),
  # you have to add _action to the name.  This is for security reasons so arbitrary
  # methods can't be called from the client.
  def alertbox_action(self, request, textToShow):
    # the event system will use this event object to call the "showalert" method
    # with a single paramter, textToShow
    return Event('showalert', textToShow)


  def change_sharedtext_action(self, request, text):
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    root.sharedtext = text
    root.save()
    return Event('receiveSharedText', text)


  def add_listitem_action(self, request, listitemtext):
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    creator = request.session.user
    listitems = root.search1(name="listitems")
    item = datagate.create_item(creatorid=creator.id, parentid=listitems.id)
    item.text = listitemtext
    item.save()
    return Event('receiveListItem', item.id, item.text)


  def delete_listitem_action(self, request, id):
    item = datagate.get_item(id)
    item.delete()
    return Event('receiveDeleteItem', id)


  def add_listitem2_action(self, request):
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    creator = request.session.user
    listitems = root.search1(name="listitems")
    item = datagate.create_item(creatorid=creator.id, parentid=listitems.id)
    # since we are using a form, we have to get the form values in the normal way
    item.text = request.getvalue('listitemtext2', '')
    item.save()
    return Event('receiveListItem', item.text)
    
    
  def send_text_area_action(self, request, dest, ar):
    return Event('receiveTextArea', dest, ar)


  def send_var_type_action(self, request, v):
    print "Variable sent to server; type is", type(v), "value is", v
    return Event('receiveType', v)
    

  #######################################
  ###   Window initialization methods

  def get_initial_events(self, request, rootid):
    '''Retrieves a list of initial javascript calls that should be sent to the client
       when the view first loads.  Typically, this is a series of add_processor
       events.'''
    root = datagate.get_item(rootid)
    events = []
    # the shared text 
    if root.getvalue('sharedtext'):
      events.append(Event('receiveSharedText', root.sharedtext))
    # the shared list
    for child in root.search1(name="listitems"):
      events.append(Event('receiveListItem', child.id, child.text))
    return events


  def initialize_activity(self, request, new_activity):
    '''Called from the Administrator.  Sets up the activity'''
    BaseView.initialize_activity(self, request, new_activity)
    creator = request.session.user
    listitems = datagate.create_item(creatorid=creator.id, parentid=new_activity.id)
    listitems.name = 'listitems'
    listitems.save()
    
