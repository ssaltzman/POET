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

# This file holds all of the constants for the program.  These must be set
# before the GroupMind server will run correctly.
# After setting the variables here, you also must run InitDB to create the 
# database tables

# Important: for those unfamiliar with Python, white space *is* important.
# Be sure not to change the amount of white space before each line (i.e.
# the tabbing).

import urllib, os, os.path, sys, logging, base64

VERSION = '2010.07.14'

def join(path1, path2):
  '''Joins two paths together (always with forward slash for web urls -- windows os.path.join puts a backslash!)'''
  if path1 == None and path2 == None:
    return ''
  if path1 == None:
    return path2
  if path2 == None:
    return path1
  if len(path2) > 0 and path2[0] == '/':
    return '/'.join([path1, path2[1:]])
  return '/'.join([path1, path2])

####################################
###   You probably only need to customize the following variable:

# The root directory of the program
#script_path = os.path.dirname(sys.argv[0])
script_path =  '~/GroupMind' 
gm_HOME = '..'
#os.path.join('..', script_path)


# The logging level to use (CRITICAL, ERROR, WARNING, INFO, DEBUG)
# For production use, set to logging.INFO
# For development use, set to logging.DEBUG
#LOG_LEVEL = logging.DEBUG
LOG_LEVEL = logging.INFO
LOG_FILE = os.path.join(gm_HOME, 'logs', 'debug.log')
#LOG_FILE = join(GROUPMIND_HOME, 'logs\debug.log')


####################################
###   Web Server Configuration   ###
####################################


# The server interface to bind to.  Most computers can leave this blank.
# It only matters if you have two network cards (i.e. two IP addresses)
IP = ''

# The server port to listen on.  
PORT = 8002

# Request log file - use empty string for no log
REQUEST_LOG_FILE = os.path.join(gm_HOME, 'logs', 'request.log')

# Where the data is kept. You can change this as needed
DATA_DIRECTORY = os.path.join(gm_HOME, 'data')

# The location of the python code in the filesystem
# It must NOT end with a slash
APP_HOME = os.path.join(gm_HOME, 'code')

# The location (in the filesystem) of the web root files
# It must NOT end with a slash
WEB_ROOT = os.path.join(gm_HOME, 'webroot')

# The url path to the program html and graphics
# This is used for links created in the dynamic HTML
# It should begin with a slash
WEB_PROGRAM_URL = "/GroupMind"

# The CGI-BIN part of the request
# You should *not* modify this as it shouldn't really change
# It should begin with a slash
CGI_BIN = '/gm-cgi'

# The url path to the CGI program
# This is used for links created in the dynamic HTML
# It must not end with a slash
CGI_PROGRAM_URL = join(CGI_BIN, '/GroupMind.py')

# The amount of time between server polls for new or changed data
# A time less than 2 seconds may poll too quickly and close the outgoing
# pipe before data can be sent form the server.  Be careful with 
# setting values too short
POLLING_TIME_IN_SECONDS = 10

# Whether we're in debug mode or not.  It is very important that
# debug mode is not turned on for production because sessions are
# not cleaned from memory
DEBUG = False

# Whether the server use threads to parallelize client calls.
# Threading significantly increases the scalability of the server,
# but it takes more memory and processing time.  If you're in a small 
# group (<10 people), you may want to turn threading off.  Leave it
# on in most cases.
THREAD_REQUESTS = False

# The period of time after which a non-active session times out
# (In seconds)
SESSION_EXPIRATION_TIME = 10# * 60  # 30 minutes



################################################################
###   Most users can stop modifying values here.  Only the   ### 
###   ones above are required for the program to run.  The   ###
###   values following simply allow program customization.   ###
################################################################


# special characters in html to convert in user comments
# this disables javascript, embedded html, and other nusances users think is funny :)
html_characters = [
  ('&', '&amp;'),  # must go first
  ('"', '&quot;'), 
  ("'", '&#39;'), 
  ('<', '&lt;'),   
  ('>', '&gt;'),  
  ('(', '&#40;'),
  (')', '&#41;'),
  ('{', '&#123;'),
  ('}', '&#125;'),
]
html_conversions = '' # used in the HTML_STYLE below
for ch in html_characters:
  html_conversions += "      st = replaceAll(st, '\\" + ch[0] +"', '" + ch[1] + "');\n"

#####################
###   HTML Skin   ###
#########,###########
# Modify this (including the skin.css file) if you want to change the skin of the program
# Because this text is inlaid into Javascript functions, it is extremely important that
# any double quotes (") not used.

# we read the CSS style file to embed within web pages or browsers retrieve it with
# each request, which is unnecessary load on the server
#css_file = open(WEB_ROOT + WEB_PROGRAM_URL + "skin.css")
#HTML_CSS = css_file.read()
#css_file.close()
#HTML_CSS = '@import "' + WEB_PROGRAM_URL + 'skin.css"'

COLOR_VERY_DARK = '#000033'
COLOR_DARK = '#0055AA'
COLOR_MEDIUM = '#0099CC'
COLOR_LIGHT = '#99CCFF'
COLOR_VERY_LIGHT = '#DDD'
COLOR_WHITE = '#FFFFFF'

HTML_TITLE = "POET powered by GroupMind"

HTML_STYLE = '<link type="text/css" rel="stylesheet" href="/GroupMind/layout.css" />'
# utility functions that are included in every page
HTML_HEAD_NO_CLOSE =  "<html><head>" + HTML_STYLE + "<title>" + HTML_TITLE + "</title>"
HTML_HEAD = HTML_HEAD_NO_CLOSE + "</head>"
# the following are for non-main view windows
HTML_BODY_NO_CLOSE = "<body"
HTML_BODY = HTML_BODY_NO_CLOSE + ">"


  
  
################################################################
###   Javascript encoding and decoding routines

# this is the python version of the Javascript decode defined above
# encoding and decoding is used in two places:
# 1: it is used to store values into the database's data field
# 2: it is used to encode values going to and from the client
alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890";
qualifier = "_";
base = 16;
pad = 4;
def decode(st):
  '''Decodes an encoded text (see the javascript above)'''
  try:
    newst = "";
    i = 0
    while i < len(st):
      if st[i] == qualifier and len(st) >= i + pad + 1:
        newst += chr(int(st[i+1: i+pad+1], base))
        i += pad
      else:
        newst += st[i]
      i += 1
    return newst
  except:
    return st
    
    
def encode(st):
  '''Encodes a string (see the javascript above)'''
  try:
    newst = ''
    for ch in str(st):
      if alphanumeric.find(ch) >= 0:
        newst += ch
      else:
        h = hex(ord(ch))[2:]  # take off the 0x
        newst += qualifier 
        for i in range(len(h), pad):
          newst += '0'
        newst += h
    return newst
  except:
    return st
  

def gm_arg_decode(st):
  '''Decodes an argument (variable) that was encoded on the Javascript
     side.'''
  def _gm_arg_decode(index):
    code = st[index]
    index += 1
    if code == 'a' or code == 'd': # an array
      ar = []
      while index < len(st) and st[index] != "-":
        index, part = _gm_arg_decode(index)
        ar.append(part)
      index += 1
      if code == 'a':  # a regular JS array/python list
        return index, ar
      else:  # a JS associative array/python dictionary
        return index, dict([ (ar[i], ar[i+1]) for i in range(0, len(ar), 2) ])
      
    else:
      pos = st.find('-', index)
      ret = decode(st[index:pos])
      index = pos+1
      if code == 'b': # boolean
        return index, bool(ret)
      elif code == 'i': # integer
        return index, int(ret)
      elif code == 'f': # float
        return index, float(ret)
      else : # default to a string
        return index, ret
      
  return _gm_arg_decode(0)[1]
    

def html(st): 
  '''Replaces all html entity characters with their &code;'''
  for ch in html_characters:
    st = st.replace(ch[0], ch[1])
  return st


##################################
###   Logging routines
###    Example: Constants.log.debug('msg') 

log = logging.getLogger('MainLog')
log.setLevel(LOG_LEVEL)
logformat = logging.Formatter('%(asctime)s %(filename)-15s %(lineno)-4d %(message)s', '%m/%d/%y %H:%M:%S')
console = logging.StreamHandler()
console.setFormatter(logformat)
log.addHandler(console)
filelog = logging.FileHandler(LOG_FILE)
filelog.setFormatter(logformat)
log.addHandler(filelog)

# add some basic logging information that we started up
log.info('===   GroupMind version ' + VERSION + ' started   ===')
