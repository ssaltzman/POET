Please turn on word wrap in your editor to read this documentation easier.


GroupMind is a groupware application that uses DHTML to dynamically change client interfaces without refresh.  It's primary purpose is to record ideas in group meetings and to bring teams to consensus through idea generation and voting screens.  It is built upon the ideas of abstract data items and modularized views.  GroupMind is a pure Python program, and it should run on any operating system that runs Python.  This includes Linux, Windows, Mac OS X, and many other operating systems.  It requires Python version 2.2+.


The LICENSE.TXT file declares the license of this software.  Source code is included with the application to help users in debugging problems and to allow users to add new functionality that meets their needs.  GroupMind is released under the GNU General Public License (GPL).  The GPL is a protective and restrictive license.  You may not use this code in any publicly-available application that is not also released under the GPL.  It doesn't matter whether you charge or don't charge money for your application.  You are required to release under the GPL or you may not use this code in any way.  I respectfully ask that you send any changes or bug fixes to me so I can integrate them back into the original source.


If you find problems with the application, please contact its author, Dr. Conan C. Albrecht <conan@warp.byu.edu>.



INFORMATION FOR PROGRAMMERS:


1. Please read the comments at the beginning of datagate.py to understand the data structure.


2. The application uses the request.cgi_href() and request.cgi_form() for all links and forms.  Use this throughout.  These methods use what I call parameter passthrough, which means that all parameters are passed automatically from request to request.  The benefit to this is parent windows can send parameters to views that are many frames deep because each frame keeps passing parameters automatically.  This effect vastly simplifies communication between views.

Certain parameter names are reserved because they are used by the event system, view architecture, or data structure.  Many of these parameters are not passed through (see dont_pass_params in Constants.py for which ones).  The reserved parameters are as follows:

Do not use the following:
  initial_events - used internally by the event system
  password - used during login only
  username - used during login only
  windowid - the id of a client window -- used to pass events to windows
  z - stores the session id of each client

Use the following to enable functions such as events, etc:
  action - you may use this to specify actions to be performed, has no inherent meaning ouside of an individual view
  event_type - the event to process (add, edit, remove, copy, paste)
  itemid - the id of an item to be acted upon -- use during edit or delete events
  item_initializer - specifies a view to initialize an item upon creation -- use when creating an item (add event)
  rootid - the id of the root item in a window -- use when instantiating a subframe
  parentid - the parent id of an item (the root id in a flat view such as Commenter) -- use when creating a new item (add event)
  previousid - the previous sibling id of an item -- use when creating or moving an item (add event)
  sessionattribute - you may use this to store attributes in the session


3. Please read the Events.py file for information about what is required for each type of event to be done.


4. All views are stored in the views directory.  They always extend BaseView and are automatically discovered by BaseView.py upon program start.  Please read BaseView.py for information on special functions that all views should implement.

5. Views are singletons -- i.e. the same objects are shared by all requests.  Don't store request-related information in the view itself or you'll have data synchronization issues between different requests.  Store request-related information in the request object.  The views are singletons so they use less memory and are faster (they are created once at app startup).  This is patterned after the Java servlet model.  




COMMON PROGRAMMING PROBLEMS:


1. TypeError: list objects are unhashable

This error usually occurs because two values for a parameter are sent through to the server.  For example, on the following line from views/MeetingHome.py, notice how the view and rootid parameters
are added to the href *outside* of the cgi_href() method:

parent.activity.location.href = "''' + request.cgi_href() + '''&view=" + views[activityid] + "&rootid=" + activityid;

Since parameters are passed through to new requests, the cgi_href() method will add the current view and current rootid to the href string.  Then, the line adds *another* view and rootid.  The presence of both in the string cause the CGI form to return a list instead of a value.  The way to solve this is the following call:

parent.activity.location.href = "''' + request.cgi_href(view=None, rootid=None) + '''&view=" + views[activityid] + "&rootid=" + activityid;

Notice how the cgi_href() method call now includes view=None and rootid=None.  This tells the method not to include them automatically because they are None.

Anytime you add extra parameters to a url that are not included in the cgi_href call directly, you
need to do this.  It is the drawback of having automatic parameter passthrough.  I feel the 
advantages outweigh the disadvantages.



