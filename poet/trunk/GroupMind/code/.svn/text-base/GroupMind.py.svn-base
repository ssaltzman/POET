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

#
#  This is the main program file for GroupMind.  All requests come through here.
#  Currently, requests come in from run_GroupMind.py (if running standalone)
#  or from GroupMind.py (if running within FastCGI [preferred]).
#

import BaseView
import Constants
import Directory
import Events
import datagate
import time
import traceback
import urllib


class Request:
  '''A new one of these is created for each request that comes through.'''
  
  def __init__(self, request, out, environment, field_storage, cgi_method):
    self.request = request
    self.out = out
    self.env = environment
    self.form = field_storage
    self.method = cgi_method

  
  def handle_cgi_request(self):
    '''Handles a cgi request.  This is the main entry point for client requests,
       whether POST or GET, that are cgi-bin requests.  They all share the
       same memory space (i.e. this singleton object).'''

    # parse the form parameters to the form object
    # if a post request, encode everything (post requests can't encode on the client side because they come from forms)
    # get requests should encode on the client side (to handle special characters in the URL)
    if self.method.lower() == 'get':
      for item in self.form.list:
        item.value = Constants.decode(item.value)
        
    # set the window id
    self.windowid = self.getvalue('global_windowid')
    
    # send the headers
    self.send_headers()
      
    try:

      # get the view      
      viewst = self.getvalue('global_view', 'meetingchooser').lower()
      
      # get the session, if there is one
      self.session = Directory.get_session(self.form.getvalue('z', ''))
        
      # if session is none, try logging the user in based upon their username and password parameters
      if self.session == None:
        self.session = Directory.login(self.form.getvalue('username', ''), self.form.getvalue('password', ''))
      
      # if the view is login, log the session out
      if (viewst == 'login' or viewst == 'logout') and self.session != None:
        Directory.logout(self.session)
        self.session = None
  
      # if session is still None, send them to the login page
      if self.session == None: 
        viewst = 'login'
       
      # process actions
      if self.session:
        Events.process_actions(self)
  
      # send events xml or send to view processing
      if self.getvalue('gm_internal_action') == 'send_events_xml':
        Events.send_events_xml(self)

      else:
        # get the view
        if not BaseView.views.has_key(viewst):
          self.writeln("<html><body>Error!  No view named " + viewst + " found.</body></html>")  
          return
        view = BaseView.views[viewst]
        self.view = view
        
        # send processing to the view
        Constants.log.debug("Sending processing to view: " + viewst)
        view.handle_request(self, viewst)

    except:
      self.writeln('<html><body>')
      self.writeln('<hr>')
      self.writeln('<b>The following error has occurred in the GroupMind application:</b>')
      self.writeln('<pre><tt>')
      traceback.print_exc(file=self.out)
      traceback.print_exc()
      self.writeln('</pre></tt>')
      self.writeln('</body></html>')
          

    
  #####################################################
  ###   Conveneience method to make things easier  
    
  def write(self, str=''):
    '''Convenience method that prints a line to the client'''
    self.out.write(str)


  def writeln(self, str=''):
    '''Convenience method that prints a line to the client'''
    self.out.write(str)
    self.out.write('\n')
    
    
  def flush(self):
    '''Convenience method that flushes the client output stream'''
    self.out.flush()
    
    
  def getvalue(self, name, default=None):
    '''Convenience method to get a form value from the request form'''
    return self.form.getvalue(name, default)
    
    
  def getlist(self, name):
    '''Convenience method to get a form value as a list from the request form.  Right now this
       method goes directly to request.form and bypasses any values set with request.setvalue(...)'''
    return self.form.getlist(name)
    
    
  def send_headers(self):
    '''Sends the headers for dynamic HTML'''
    if self.getvalue('gm_contenttype', '') == '':
      self.writeln('Content-Type: text/html')
    else:
      #Constants.log.debug("Content-Type overridden by " + str(self.getvalue("global_view")) + ".  Content-Type: " + self.getvalue("gm_contenttype"))
      self.writeln("Content-Type: " + self.getvalue('gm_contenttype'))
    
    if not self.getvalue('contentdisposition', '') == '':
      self.writeln("Content-Disposition: attachment; filename="+self.getvalue('contentdisposition'))
      
    self.writeln('Expires: ' + time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()))
    self.writeln() # ends the headers
    
    

  def get_global_parameters(self, params):
    '''Adds the global parameters to make up request string parameters'''
    parameters = {}
    # first add the global arguments from last time
    for key in self.form.keys():
      if key[:7].lower() == 'global_':
        value = self.form.getvalue(key)
        if value != None and value != '':
          parameters[key] = value
          
    # next add the windowid if we have one (it may have been created in BaseView.handle_request)
    if self.windowid:
      parameters['global_windowid'] = self.windowid
        
    # next add everything that is specifically added this time
    for key in params:
      if params[key] != None and params[key] != '':
        parameters[key] = params[key]
      elif parameters.has_key(key):  # if it is explicitly sent as None, we remove it
        del parameters[key]
        
    # add the session
    if self.session:
      parameters['z'] = self.session.id
    
    # turn into a list of lists, then return
    #Constants.log.info("PARMS: " + str(parameters.items()))
    return parameters.items()
    
    
        
  def cgi_href(self, **kargs):
    '''Convenience method to return the a form tag with parameters, z, and view'''
    items = ['='.join([urllib.quote(str(field)), urllib.quote(str(value))]) for field, value in self.get_global_parameters(kargs)]
    return Constants.CGI_PROGRAM_URL + '?' + ('&'.join(items))
    
      
  def cgi_form(self, **kargs):
    '''Convenience method to return the <form> tag with parameters, z, and view
       Special names are as follows:
         name = the name of the form
         method = the request method (GET, POST, etc.)
         enctype = the encoding type
       Any other parameters are sent as fields.
    '''
    # build the form tag
    form = "<form action='" + Constants.CGI_PROGRAM_URL + "'"
    if not kargs.has_key('method'): # ensure we have method
      form += " method='POST'"
    for key in [ 'method', 'name', 'enctype' ]:
      if kargs.has_key(key) and kargs[key] != None:
        form += " " + key + "='" + kargs[key] + "'"
    form += ">\n"
    # add hidden inputs for all other parameters
    for field, value in self.get_global_parameters(kargs):
      form += "<input type='hidden' name='" + str(field) + "' value='" + str(value) + "'>\n"
    return form
    

  def cgi_multipart_form(self, **kargs):
    '''Convenience method to return the <form> tag with parameters, z, and view.
       This method is useful for use when uploading files (multipart/form-data).
       Special names are as follows:
         name = the name of the form
         method = the request method (GET, POST, etc.)
    '''
    kargs['enctype'] = 'multipart/form-data'
    return self.cgi_form(**kargs)


