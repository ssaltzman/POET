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
#  This is the main boostrap file for running GroupMind directly from
#  the command line.  This method requires no extra modules.  It includes
#  its own web server.  Just run 'python run_GroupMind.py' from the 
#  command line.
#
#  Note that this method of running GroupMind should only be used for
#  debugging.  The FastCGI module (see GroupMind.py) is the preferred
#  way to run GroupMind as it is significantly faster.
#

import Constants
import GroupMind, Directory
from SocketServer import BaseServer
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from OpenSSL import SSL
import threading, cgi, os, posixpath, urllib, traceback, time, socket

CGI_BIN = Constants.CGI_BIN
CGI_BIN_LEN = len(CGI_BIN)
ONE_DAY_IN_SECONDS = 60 * 60 * 24
log_sync_lock = threading.RLock()

class SecureHTTPServer(HTTPServer):
  def __init__(self, server_address, HandlerClass):
    BaseServer.__init__(self, server_address, HandlerClass)
    ctx = SSL.Context(SSL.SSLv3_METHOD)
    ctx.set_options(SSL.OP_NO_SSLv2)
    ctx.set_cipher_list('HIGH:!DSS:!aNULL@STRENGTH')
    #server.pem's location (containing the server private key and
    #the server certificate).
    fpem = 'server.pem'
    ctx.use_privatekey_file (fpem)
    ctx.use_certificate_file(fpem)
    self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
                                                    self.socket_type))
    self.server_bind()
    self.server_activate()


# a new one of these is created for each request that comes in
# this is the main class of the entire application
# the main loop goes through here
class StandaloneRequest(SimpleHTTPRequestHandler):

  def setup(self):
    self.connection = self.request
    self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
    self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)

  def do_GET(self):
    '''Receives the GET request'''
    self.method = 'get'
    self.go()
    
    
  def do_POST(self, method='post'):
    '''Receives the POST request'''
    self.method = 'post'
    self.go()
    

  def go(self):    
    '''Main loop. If a CGI, calls the shared handle_cgi method.
       If a normal request, calls the shared handle_regular method.'''
    # send to processing   
    if Constants.THREAD_REQUESTS:
      thread = threading.Thread(target=self.run)
      thread.setDaemon(1)
      thread.start()
      
    else:  
      self.run()
    
    
  def run(self):
    '''Method that runs when this thread is started'''
    try:
      # test whether a cgi script
      if self.requestline.find(Constants.CGI_PROGRAM_URL) >= 0:
        self.wfile.write('HTTP/1.0 200 OK\n')
        env = self.get_env()
        fields = cgi.FieldStorage(environ=env, fp=self.rfile)
        request = GroupMind.Request(self, self.wfile, env, fields, self.method)
        if Constants.REQUEST_LOG_FILE:
          self.log_it(request)
        request.handle_cgi_request()
        
      else: # serve a file (my superclass is good at that)
        SimpleHTTPRequestHandler.do_GET(self)
  
      self.new_finish() # closes the connections
    except (IOError): # thrown when the client presses top or we refresh too quickly
      print "Client pipe on " + str(self.client_address) + " closed prematurely."
    
    
  
  def log_it(self, request):
    '''Logs the information in a request'''
    # first create the request
    info = []
    info.append('Date: ' + time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
    session = Directory.get_session(request.getvalue('z', ''))
    if session and session.user:
      info.append('User: ' + session.user.username)
    for key in request.form.keys():
      info.append(key + ": " + str(request.getvalue(key)))
    
    # log to the file
    log_sync_lock.acquire()
    try:
      f = open(Constants.REQUEST_LOG_FILE, 'a')
      f.write('\n'.join(info) + '\n\n')
      f.close()
    finally:
      log_sync_lock.release()
    

  def finish(self):
    '''We have to override finish because we're threaded now and the standard
       SocketServer closes our connection in finish!'''
    pass
    
    
  def new_finish(self):
    '''Our replacement finish method'''
    SimpleHTTPRequestHandler.finish(self)


  def translate_path(self, path):
    """Translate a /-separated PATH to the local filename syntax.
       This is overridden from the superclass because SimpleHTTPRequestHandler
       uses the current working directory to serve the files and I want to
       change that"""
    path = posixpath.normpath(urllib.unquote(path))
    words = path.split('/')
    words = filter(None, words)
    path = Constants.WEB_ROOT
    for word in words:
      drive, word = os.path.splitdrive(word)
      head, word = os.path.split(word)
      if word in (os.curdir, os.pardir): 
        continue
      path = os.path.join(path, word)
    return path      


  def get_env(self):
    '''Creates the environment for the cgi module'''
    # this part shamelessly ripped from CGIHTTPRequestHandler.is_cgi()
    path = self.path
    self.cgi_info = path[:CGI_BIN_LEN], path[CGI_BIN_LEN+1:]
    
    # this part shamelessly ripped from CGIHTTPRequestHandler.run_cgi()
    # I modified a few things (such as self==>request), but not much is changed
    dir, rest = self.cgi_info
    i = rest.rfind('?')
    if i >= 0:
      rest, query = rest[:i], rest[i+1:]
    else:
      query = ''
    i = rest.find('/')
    if i >= 0:
        script, rest = rest[:i], rest[i:]
    else:
        script, rest = rest, ''
    scriptname = dir + '/' + script
    scriptfile = self.translate_path(scriptname)

    # Reference: http://hoohoo.ncsa.uiuc.edu/cgi/env.html
    # XXX Much of the following could be prepared ahead of time!
    env = {}
    env['SERVER_SOFTWARE'] = self.version_string()
    env['SERVER_NAME'] = self.server.server_name
    env['GATEWAY_INTERFACE'] = 'CGI/1.1'
    env['SERVER_PROTOCOL'] = self.protocol_version
    env['SERVER_PORT'] = str(self.server.server_port)
    env['REQUEST_METHOD'] = self.command
    uqrest = urllib.unquote(rest)
    env['PATH_INFO'] = uqrest
    env['PATH_TRANSLATED'] = self.translate_path(uqrest)
    env['SCRIPT_NAME'] = scriptname
    if query:
        env['QUERY_STRING'] = query
    host = self.address_string()
    if host != self.client_address[0]:
        env['REMOTE_HOST'] = host
    env['REMOTE_ADDR'] = self.client_address[0]
    # XXX AUTH_TYPE
    # XXX REMOTE_USER
    # XXX REMOTE_IDENT
    if self.headers.typeheader is None:
        env['CONTENT_TYPE'] = self.headers.type
    else:
        env['CONTENT_TYPE'] = self.headers.typeheader
    length = self.headers.getheader('Content-Length')
    if not length:
      length = len(query)
    env['CONTENT_LENGTH'] = length
    accept = []
    for line in self.headers.getallmatchingheaders('accept'):
        if line[:1] in "\t\n\r ":
            accept.append(line.strip())
        else:
            accept = accept + line[7:].split(',')
    env['HTTP_ACCEPT'] = ','.join(accept)
    ua = self.headers.getheader('user-agent')
    if ua:
        env['HTTP_USER_AGENT'] = ua
    co = filter(None, self.headers.getheaders('cookie'))
    if co:
        env['HTTP_COOKIE'] = ', '.join(co)   
    return env


    
  def log_message(self, format, *args):
    '''Disable/enable logging of requests (overrides BaseHTTPServer.log_message)'''
    if Constants.DEBUG:
      SimpleHTTPRequestHandler.log_message(self, format, *args)
      
      
  def address_string(self):
    '''Overrides BaseHTTPServer.address_string because that method can be extremely slow!'''
    # instead of looking up the name, simply return the address the client sent
    return self.client_address[0]

   
    

def main():
  '''Main loop of the program.  Called from below or from run_daemon.py'''
  handler_class = StandaloneRequest
  server_address = (Constants.IP, Constants.PORT)
  httpd = SecureHTTPServer(server_address, handler_class)
  Constants.log.info("Waiting for connections on" + str(server_address))
  try:
    while 1:
      try:
        httpd.handle_request()
      except KeyboardInterrupt:
        raise
      except:
        traceback.print_exc()
  except KeyboardInterrupt:
    Constants.log.info('Break.  Thanks for using GroupMind!')


##############################################
###  Standalone startup code 

if __name__ == '__main__':
  main()
