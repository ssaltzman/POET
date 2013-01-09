#/usr/bin/python

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

# Defines User, Group, and Session classes

import datagate
import TimedDict
import Constants
import Events
import GUID
import time
import threading
import sys
import xml.dom.minidom

root_item = datagate.get_item('z') # root item has a special id
users_item = root_item.search1(name='users')
meetings_item = root_item.search1(name='meetings')

##########################################
###   User accessors

USER_FIELDS = [ 'name', 'email', 'password', 'username', 'title', 'office', 'work', 'home', 'mobile', 'fax', 'comments' ]
  
def get_users():
  '''Returns all users in the database as a list of items'''
  return users_item.search(active='1')
  
  
def get_user(id):
  '''Retrieves the User by id'''
  return datagate.get_item(id)
  
  
def get_user_by_data(username, password):
  '''Retrieves the User by username and password.'''
  for item in users_item.search(username=username):
    if item.password == password and item.active == '1':
      return item
  return None
  
  
def create_user(creatorid):
  '''Creates a new user'''
  user = datagate.create_item(creatorid=creatorid, parentid=users_item.id)
  for key in USER_FIELDS:
    setattr(user, key, '')
  user.superuser = '0'
  user.active = '1'
  user.save()
  return user
  
    
    
#######################################
###   Sessioning and eventqueue classes
    
class EventQueue:
  '''A simple queue that holds events for a window'''
  def __init__(self, windowid):
    self.windowid = windowid
    self.events = []
    self.lock = threading.RLock()
    
  def add_event(self, event):
    self.lock.acquire()
    try:
      if not event in self.events:  # every once in a long while, people get the same event twice!
        self.events.append(event)
    finally:
      self.lock.release()

  def pop_all(self):
    '''Retrieves all events from the queue and then clears the queue'''
    self.lock.acquire()
    try:
      events = self.events
      self.events = []
      return events
    finally:
      self.lock.release()
    
  def __eq__(self, other):
    try:
      return self.windowid == other.windowid
    except:
      return 0
    
    
    
  
class Session:
  '''A session that authenticates a user on each call after login'''
  def __init__(self, user):
    self.id = GUID.generate()
    self.started = time.time()
    self.user = user
    self.listeners = {}    # windows that are listening for events
    self.lock = threading.RLock()
    
    
  def process(self, rootid, event, windowid=None):
    '''Processes an event for this session'''
    self.lock.acquire()
    try:
      if self.listeners.has_key(rootid):
        for listener in self.listeners[rootid]:
          if windowid == None or listener.windowid == windowid: # for initial events, only sends to the exact windowid that is loading
            listener.add_event(event)
    finally:
      self.lock.release()
      
      
  def add_event_queue(self, windowid, rootid):
    '''Adds an event queue for this rootid and windowid'''
    self.lock.acquire()
    try:
      eventqueue = EventQueue(windowid)
      # add to my data structures
      if self.listeners.has_key(rootid):
        if not eventqueue in self.listeners[rootid]:
          self.listeners[rootid].append(eventqueue)
      else:
        self.listeners[rootid] = [ eventqueue ]
    finally:
      self.lock.release()
            
  
  def get_events(self, windowid, rootid):
    '''Gets the events that have posted for this windowid and data item id'''
    self.lock.acquire()
    try:
      if self.listeners.has_key(rootid):
        for event_queue in self.listeners[rootid]:
          if event_queue.windowid == windowid:
            return event_queue.pop_all()
      return [] # default
    finally:
      self.lock.release()
    
    
# called when a session is removed
def sessionRemoved(key, session):
  Events.remove_session_listeners(session.id)
  

# the singleton sessions variable (holds all current sessions)
sessions = TimedDict.TimedDict(listener=sessionRemoved)
  
  
# helper methods
def login(username, password):
  '''Verifies a password and returns a Session for this user'''
  # get the user
  user = get_user_by_data(username, password)

  # if user is none, send an empty session back
  if user == None:
    return None  
  
  # create a session and return
  session = Session(user)
  sessions[session.id] = session
  return session
  
  
def logout(session):
  '''Invalidates the given session'''
  del sessions[session.id]
  

def get_session(session_id):
  '''Returns the session if it is in the cache, None otherwise'''
  if sessions.has_key(session_id):
    return sessions[session_id]
  return None
  
  
def is_online(userid):
  '''Returns whether the given user is online at the moment
     A user is online if he has an open session.  Sessions are closed after 30 minutes
     of inactivity or after explicit logouts by users.
  '''
  for session in sessions.values():
    if session.user.id == userid:
      return 1
  return 0
    
  
#################################
###   Meeting accessors  

def get_meetings():
  '''Returns all meetings in the database as a list of items'''
  return datagate.get_child_items(meetings_item.id)
    
  
def get_meeting(id):
  '''Retrieves the Meeting by id'''
  return datagate.get_item(id)


def create_meeting(name, view, creatorid):
  '''Creates a new meeting given the name'''
  meeting = datagate.create_item(creatorid=creatorid, previousid='last', parentid=meetings_item.id)
  meeting.name = name
  meeting.view = view
  meeting.save()
  return meeting
  
  
def import_meeting(doc, creatorid):
  '''Creates a meeting by importing an exported xml document.  The document should
     be created before this method is called.'''
  # get the meetingdata and userdata nodes
  meetingnode = None
  usersnode = None
  old_root_guid=''
  for child in doc.documentElement.childNodes:
    if child.nodeName == 'MeetingData':
      meetingnode = child
    elif child.nodeName == 'UserData':
      usersnode = child
  assert meetingnode != usersnode != None, 'Error importing meeting.  Cannot find the meeting and/or users nodes.'
  
  # import the meeting subtree and add to the meetings list
  meeting = datagate.import_xml(meetingnode)
  meeting.parentid = ''
  meeting.rewrite_ids()
  meeting.save(deep=1)
  meetings_item.insert_child(meeting)
  meetings_item.save()
  
  # importing is a little more complex than copying a meeting because
  # the import might come from a different machine.  Since it does, some users
  # may not be available on this machine.  We have to recreate these users here.
  # step through the nodes and compile a list of users who created objects but are
  # not in this system
  # import the users into a set of items
  
  #PROBLEM:  What happens when the users are assigned to a strikeCom team?  That we can fix, but now we have 2 superusers, both named root.

  users = datagate.import_xml(usersnode)
  for user in users:
      if user.username=='root':
        old_root_guid = user.id
  
  def check_for_lost_users(item): 
    # check for this user
    sc_user_id=''
    try:
      sc_user_id = item.user_id  # check to see if the item is a strikecom team member
    except AttributeError:
      pass
    if users_item.get_child(item.creatorid) == None: # creator is not in the current users list
      importeduser = users.get_child(item.creatorid)
      if importeduser != None and importeduser.username!='root': 
        importeduser.creatorid = creatorid
        users_item.insert_child(importeduser)
        importeduser.save()
        users_item.save()
        
    if users_item.get_child(sc_user_id) == None and sc_user_id != '': # the strikecom member user_id is not in the current users list
      importeduser = users.search1(id=sc_user_id)
      if importeduser != None and importeduser.username!='root': # check for root here also incase he has been assigned to a team 
        importeduser.creatorid = creatorid
        users_item.insert_child(importeduser)
        importeduser.save()
        users_item.save()        
    
    # recurse to children
    for child in item.get_child_items():
      check_for_lost_users(child)
      
  check_for_lost_users(meeting)

  meeting.get_parent().replace_root_ids(old_root_guid, creatorid) #start from the root item and replace all
  meeting.get_parent().save(deep=1)
  
  # return a reference to the new meeting
  return meeting
  
  
def export_meeting(global_meetingid):
  '''Exports a meeting to an xml document'''
  # create the xml document
  doc = xml.dom.minidom.Document()
  root = doc.appendChild(doc.createElement("GroupMind"))

  # get the meeting
  meeting = datagate.get_item(global_meetingid)
  meetingroot = meeting.export().documentElement
  meetingroot.tagName = 'MeetingData'
  root.appendChild(meetingroot)
  
  # get the users
  # the users are exported in full every time so the creatorid's in the data
  # always make sense.  Upon import, they are recreated as needed.
  usersroot = users_item.export().documentElement
  usersroot.tagName = 'UserData'
  root.appendChild(usersroot)
  
  # return to the caller
  return doc


def get_group(global_meetingid, userid):
  '''Returns the group item the given user is in for the given meeting, or None if the user has no rights in the meeting'''
  meeting = datagate.get_item(global_meetingid)
  groups_item = meeting.search1(name='groups')
  for group in groups_item.get_child_items():
    if group.search1(user_id=userid) != None:
      return group
  return None
  

def get_groups(global_meetingid):
  '''Returns the groups in a given meeting as a list of items'''
  meeting = datagate.get_item(global_meetingid)
  groups_item = meeting.search1(name='groups')
  return groups_item.get_child_items()


def get_meeting_users(global_meetingid):
  '''Returns all users in the given meeting as a list of items.  The list is sorted by username.
  '''
  meeting = datagate.get_item(global_meetingid)
  groups_item = meeting.search1(name='groups')
  # using a dict ensures we don't get duplicate users (in more than one group, which is allowed)
  users = {}
  for group in groups_item.get_child_items():
    for user_link in group.get_child_items():
      users[user_link.user_id] = datagate.get_item(user_link.user_id)
  # sort and return
  user_list = users.values()
  user_list.sort(lambda a,b: cmp(a.username, b.username))
  return user_list
  
  
