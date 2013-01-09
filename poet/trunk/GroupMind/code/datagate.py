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

# This file is the gateway to data in the items table
#
# The database should not be accessed directly, but should be done through this
# file.  If the database is accessed directly, it will cause synchronization problems
# between memory-cached objects and back-end data!
#
# Questions about the data field readers might have:
#
# - Why not use a database to store everything in?
# I used to.  Everything was searchable and nicely put into a database.
# However, it had its disadvantages:
# 1. The code was buggy and fragile.  (this was the real problem)
# 2. It required installation of database drivers into python, making installation a pain.
# 3. We really didn't need the search capabilities since we really access hiearchically anyway.
#
# - How are data items saved to the filesystem?
# I'm using the shelve module to save data items by GUID.  I don't want all items in
# one dbm file since it would take forever to load and save.  I also don't want each item
# in its own file since meetings have had 100-500 items in them.  We'd quickly hit the Linux
# directory limit of 32K files per directory.  I'm not sure what the Windows limit is, but in
# any case, it's not a good solution.  Since 16^3 = 4096 (a nice number of data files), I'm
# storing items in data files named after the 3 random bits in the GUID.  For all practical 
# purposes, this equates to 1-5 items per file -- a very manageable size.
#
# - How are items related to each other?
# The items table defines a hierarchical tree of objects in parent-child relationships.
# Children are ordered by their previousids.
#
# - Why does this file deal with ids rather than real objects (for example, the del_item function)?
# Yes, I know this isn't very object oriented.  But the CGI can't pass objects.  So forms have
# to send item ids rather than real item objects.  So I matched this file to use ids as well
# to make life consistent for views, since ids are what they deal with.
#
# - How is arbitrary data set/retrieved in/from an item?
# Two ways (either is permissible):
# 1. Simply use item.field = 'value'.  Any field name that is not in the item_fields list
#    (see below) is placed into the data dictionary and saved into the data column
#    using the encoding method described above.  See the __getattr__ and __setattr__ 
#    methods for more information on how this is done
# 2. Access the data dictionary directory, as in item.__dict__['field'] = 'value'.  
#    
# On the client-side (from Javascript), you have to use item.data['field'] to get/set
# arbitrary attributes.  I haven't figured out how to make Javascript allow direct dot
# notation as Python can.

from Constants import *
import GUID
import copy
import os
import os.path
import re
import shelve
import socket
import sys
import threading
import time
import TimedDict
import xml.dom
import xml.dom.minidom
try:
  import cPickle
  pickle = cPickle
except:
  import pickle


# The number of significant GUID chars used to shelve items in the file databases
# Normally, you should not change this unless you know what you are doing
# It will result in 16^NUMBER_SIGNIFICANT_GUID_CHARS database files to store all items in
# i.e. 1 => 16 files, 2 => 256 files, 3 => 4096 files, 4 => 65K
# Note that Linux's ext3 (currently) can't store more than 32K files in a directory,
# so a value > 3 will eventually crash the program!
# The default value of 2 is usually appropriate for smaller installs, 3 for very large ones
NUMBER_SIGNIFICANT_GUID_CHARS = 2

# Ensure the shelf directory exists
if not os.path.exists(DATA_DIRECTORY):
  raise RuntimeError, 'Error, data directory as defined in Constants.py does not exist.  Have you run the Install.py program yet?'

# An in-memory cache to hold frequently-used items
# This cache is the primary means for making item retrieval and access
# efficient.  The only drawback is memory usage, which shouldn't be a problem
# unless you have an incredibly large user base.
# Each value in the map is a list [lock, item obj]
items_cache = TimedDict.TimedDict()
items_lock = threading.RLock()

##################################
###   Items class
class Item:
  '''An item in the database'''
  def __init__(self, creatorid='', parentid=''):
    '''Constructor -- called only for new Items'''
    self.id = GUID.generate()
    self.creatorid = creatorid
    self.parentid = parentid
    # ids of my children (in order)
    # do _not_ keep direct references as pickling will serialize entire trees
    self.childids = []

      
  def __repr__(self):
    return '@datagate.item ' + self.id + ': ' + str(self.__dict__)
    
    
  def getvalue(self, key, default=None):
    '''Convenience method to retrieve an attribute with a default if not found.'''
    if hasattr(self, key):
      return getattr(self, key)
    return default
    
    
  def get_data_keys(self, regexp=None):
    '''Retrieves the data keys for this item, optionally filtered by the given regular expression'''
    if regexp == None:
      return self.__dict__.keys()
    keys = []
    reg = re.compile(regexp)
    for key in self.__dict__.keys():
      if reg.match(key):
        keys.append(key)
    return keys
    
        
  def __eq__(self, other):
    try: return self.id == other.id
    except: return 0
    
    
  def __ne__(self, other):
    return not self.__eq__(other)
    
    
  def encode_data(self):
    '''Returns the encoded data string.  This is used by BaseView and Events to send events to the client.'''
    value = ''
    for key in self.__dict__.keys():
      value += '&' + encode(key) + '=' + encode(getattr(self, key))
    if value == '': value = '&&'
    else: value += "&" # pad with & on both sides
    return value    
    
    
  def save(self, deep=0):
    '''Saves this item to the database, possibly saving deep (all children)'''
    # save the changes
    lock = self._acquire_lock()
    try:
      # save everything
      s = open_shelf(self.id)
      s[self.id] = self
      s.close()
      
      # save my children
      if deep:
        for child in self.get_child_items():
          child.save(deep)

    finally:
      lock.release()
    
    
  def _acquire_lock(self):
    '''Acquires and returns the reentrant lock for this item'''
    lock = items_cache[self.id][0]
    lock.acquire()
    return lock
    
    
  def get_parent(self):
    '''Retrieves the parent of this item'''
    return get_item(self.parentid)
  
  
  def _recurse_get_child_items(self, children, deep=0, sort=None):
    '''Internal recursive method to get child items'''
    # add my children one by one
    for childid in self.childids:
      child = get_item(childid)
      if child:
        children.append(child)
        if deep:
          child._recurse_get_child_items(children, deep, sort)
      else: # child has been removed and my list hasn't been updated
        self.childids.remove(childid)
        self.save()
        
  
  def get_child_items(self, deep=0, sort=None):
    '''Convenience method to Retrieves the child items of this item'''
    children = []
    self._recurse_get_child_items(children, deep, sort)
    return children
    
    
  def __iter__(self):
    '''Allows use of "for child in item:" to iterate through children'''
    return iter(self.get_child_items())
    

  def __getitem__(self, key):
    '''Returns the numbered child'''
    return self.get_child(self.childids[key])
    
  def get_child(self, childid):
    '''Retrieves a child of this item by its id'''
    child = get_item(childid)
    if child != None and child.parentid == self.id:
      return child
    return None
    
    
  def get_creator(self):
    '''Returns the item representing the user that created this item'''
    return get_item(self.creatorid)
    
  
  def get_previous(self):
    '''Returns the previous item as determined by the ordering in my parent code'''
    parent = self.get_parent()
    myindex = parent.childids.index(self.id)
    if myindex > 0:
      return get_item(parent.childids[myindex - 1])
    return None
    
  
  def get_previousid(self):
    '''Convenience method to return the previous item's id, or '' if this is the first item'''
    previous = self.get_previous()
    return (previous and previous.id or '')
    

  def search(self, **kargs):
    '''Returns my child items that have matching values for the given key'''
    matches = []
    for child in self.get_child_items():
      match = 1
      for key, val in kargs.items():
        if not hasattr(child, key) or getattr(child, key) != val:
          match = 0
          break
      if match:
        matches.append(child)
    return matches
        
    
  def search1(self, **kargs):
    '''Returns the first matching child with the value for the given key'''
    for child in self.get_child_items():
      match = 1
      for key, val in kargs.items():
        if not hasattr(child, key) or getattr(child, key) != val:
          match = 0
          break
      if match:
        return child
    return None
    
  
  def _delete(self):
    '''Helper method (recursive) for the delete method'''
    lock = self._acquire_lock()
    try:
      # first go through and tell my children to delete themselves
      for childid in self.childids:
        child = get_item(childid)
        if child:
          child.delete()
      
      # now delete myself
      s = open_shelf(self.id)
      del s[self.id]
      s.close()
      
      # finally, delete from the items cache
      del items_cache[self.id]
      
    finally:
      lock.release()    
    
    
  def delete(self):
    '''Deletes this item and all children, including removing this item from it's parent's child list'''
    lock = self._acquire_lock()
    try:
      # remove me from my parent (this only needs to be done on the top item)
      parent = self.get_parent()
      if parent:
        parent.remove_child(self)
        parent.save()
      
      # delete my subtree tree
      self._delete()
      
    finally:
      lock.release()
    
    
  def insert_child(self, item, previousid=None):
    '''Inserts a child into this parent's child list, defaulting at the end.  
       Does not save the changes -- you must call save on the item and the newly-added child!'''
    # first remove from the parent, just in case this is a move
    self.remove_child(item)
      
    lock = self._acquire_lock()
    try:
      item.parentid = self.id
      # add to the right spot - will throw an error if previous is None or not found
      try: 
        if previousid:  # I explicitly check this because it's faster -- a lot of items are simply appended without a previousid
          self.childids.insert(self.childids.index(previousid) + 1, item.id)
        else:
          self.childids.append(item.id)
      except ValueError: 
        self.childids.append(item.id)
    finally:
      lock.release()
      
      
  def remove_child(self, item):
    '''Removes a child from this parent's child list. 
       Doesn't delete the item and doesn't save changes.  You must explicitly delete (or add to a new parent)
       and save the item and the newly-removed child!'''
    lock = self._acquire_lock()
    try:
      item.parentid = ''
      try: 
        self.childids.remove(item.id)
      except ValueError: 
        pass
    finally:
      lock.release()
      
      
  def _export(self, doc, node):
    '''Internal method to export this item's info to the parent'''
    # add my information to the node
    for key, value in self.__dict__.items():
      if not key in [ 'childids', 'data' ]:
        datanode = node.appendChild(doc.createElement('data'))
        datanode.setAttribute('name', str(key))
        # pickled version for importing back to correct type (pickled strings are already readable, so no need for other readable version)
        datanode.appendChild(doc.createCDATASection(pickle.dumps(value)))
    
    # add child nodes for my children
    for childid in self.childids:
      child = get_item(childid)
      childnode = node.appendChild(doc.createElement('child'))
      child._export(doc, childnode)
      
      
  def export(self):
    '''Exports this item (including all children) to an XML document.
       Returns the new xml document.
    '''
    # create the xml document
    doc = xml.dom.minidom.Document()
    root = doc.appendChild(doc.createElement("GroupMind"))
    
    # meta information
    meta = root.appendChild(doc.createElement('meta'))
    date = meta.appendChild(doc.createElement('exportdate'))
    date.appendChild(doc.createTextNode(time.strftime('%a, %d %b %Y %H:%M:%S')))
    ip = meta.appendChild(doc.createElement('server'))
    try:
      ip.appendChild(doc.createTextNode(socket.gethostbyname(socket.gethostname())))
    except Exception, e:
      ip.appendChild(doc.createTextNode(str(e)))
    
    # items
    itemnode = root.appendChild(doc.createElement('items'))
    self._export(doc, itemnode)

    # return the document
    return doc    
    
    
  def prettyprint(self, ofile=sys.stdout, tab=''):
    '''Pretty prints this item and all subchildren.  This method is for debugging only.'''
    ofile.write(tab + str(self))
    ofile.write('\n')
    for child in self.get_child_items():
      child.prettyprint(ofile, tab + '  ')
      
      
  def _rewrite_ids(self, parentid, guids):
    '''Helper method for rewrite_ids.  Don't call directly'''
    items_lock.acquire()
    try:
      # rewrite my id, save in cache under new id, and map old guid to new guid
      oldguid = self.id
      self.id = GUID.generate()
      self.parentid = parentid
      items_cache[self.id] = [ threading.RLock(), self ]
      guids[oldguid] = self
      
      # rewrite my children
      for i in range(len(self.childids)):
        child = get_item(self.childids[i])
        child._rewrite_ids(self.id, guids)
        self.childids[i] = child.id # now we have the new childid recorded in our child list
        
    finally:
      items_lock.release()
      
      
  def rewrite_ids(self):
    '''Rewrites the ids of this item and all its children.  This means that all ids are
       recreated, and all internal references to ids (parents, child lists, data) are
       switched to the new guids.  
       
       This method is useful during copying paths on the items tree (use export/import to
       copy, then rewrite ids so the new items don't conflict with the old).
       
       This method should not be called often.  It locks the entire system (items_lock)
       to ensure things don't go wierd.
       
       This method saves my changed id to my parent (if I have one), but does not save
       the changes to myself or my children.  Therefore, call item.save(deep=1) after this
       method (assuming you want to save the changes).
    '''
    items_lock.acquire()
    try:
      # save my old guid
      oldguid = self.id
      parent = self.get_parent()
    
      # rewrite me and everyone below me
      guids = {}
      self._rewrite_ids(self.parentid, guids)
      
      # while the new tree is intact and linked, there may be some links stored in the data
      # section that we need to switch to the new guids.  This is the purpose of the guids map
      for newitem in guids.values(): # go through all new items in the tree
        for key in newitem.__dict__.keys(): # for each data value in this item
          for oldlinkid, newlink in guids.items():
            if type(getattr(newitem, key)) == type(''):
              setattr(newitem, key, getattr(newitem, key).replace(oldlinkid, newlink.id))
      
      # rewrite in my parent, if I have one, since the loop above didn't affect items above me
      if parent:
        pos = parent.childids.index(oldguid)
        parent.childids[pos] = self.id
        parent.save()
    
    finally:
      items_lock.release()
    
  def replace_root_ids(self, old_id, new_id):
    '''
    This is used to recurse the imported meeting and replace everywhere the imported root user
    appears.  We are replacing him with the local root user.
    '''
    items_lock.acquire()
    try:
      for child in self.get_child_items():
        child.replace_root_ids(old_id, new_id)
        for key in child.__dict__.keys():
          if type(getattr(child, key)) == type([]):
            nlist = []
            for uid in getattr(child, key):
              nlist.append(uid.replace(old_id, new_id))
            setattr(child, key, nlist)  
          elif type(getattr(child,key)) == type(''):
            setattr(child, key, getattr(child, key).replace(old_id,new_id))
    finally:
      items_lock.release()
            

#################################
###   Factory methods for items

def open_shelf(id):
  '''Opens the shelf conaining the given id'''
  return shelve.open(os.path.join(DATA_DIRECTORY, id[-1 * NUMBER_SIGNIFICANT_GUID_CHARS:].lower()))


def _ping(item): 
  '''Updates the timestamp on the item'''
  get(items_cache(item.id))
  
  
def get_item(id):
  '''Retrieves an item by its id'''
  # short circuit
  if id == None or id == '':
    return None
  
  # first check the cache
  if items_cache.has_key(id):
    return items_cache[id][1]
    
  # lock it up so we can get it from the shelf
  items_lock.acquire()
  try:
    # check again now that we're locked (another thread may have placed it in the cache while we waited)
    if items_cache.has_key(id):
      return items_cache[id][1]
    
    # get it from the appropriate shelf
    # items are shelved in files named after their three random bits (allows max 4096 shelves)
    s = open_shelf(id)
    try:
      try:
         item = s[id]
         items_cache[item.id] = [ threading.RLock(), item ]
         return item
      except KeyError:
        pass
    finally:
      s.close()
      
    return None
    
  finally:
    items_lock.release()

  
def create_item(creatorid=None, parentid=None, previousid=None):
  '''Creates a new, empty item'''
  items_lock.acquire()
  try:
    # create the new item
    item = Item(creatorid, parentid)
    items_cache[item.id] = [ threading.RLock(), item ]
    item.save()
     
    # add to the parent in the right location (this makes it visible to views)
    parent = get_item(parentid)
    if parent:
      parent.insert_child(item, previousid)
      parent.save()

    return item
  finally:
    items_lock.release()
  
  

def get_child_items(parentid, deep=0, sort=None):
  '''Convenience method to get the child items of a parent (mostly for backwards compatability to older views)'''
  return get_item(parentid).get_child_items(deep=deep, sort=sort)


def del_item(id):
  '''Convenience method to delete an item (including subtree)'''
  get_item(id).delete()
  

def copy_deep(oldid, newparentid):
  '''Copies an item (deeply) to a child of the newparentid.  All internal GUIDs are
     converted to new GUIDs, and all references are moved as well.
     Returns the new item.  The algorithm is not fast, but it is pretty robust.  I assume that
     copying doesn't happen very often -- since I acquire the master items lock, it basically
     locks the system while it completes.'''
  items_lock.acquire()
  try:
    # copy using import and export
    item = get_item(oldid)
    doc = item.export()
    newitem = import_xml(doc.documentElement)
    newitem.parentid = ''
    newitem.rewrite_ids()
    newitem.save(deep=1)

    # graft into tree under newparent
    newparent = get_item(newparentid)
    newparent.insert_child(newitem)
    newparent.save()

    # return the new item
    return newitem
    
  finally:
    items_lock.release()
    

def _import_xml(node):
  '''Internal helper for import_xml.  Do not call directly'''
  items_lock.acquire()
  try:
    # create a new item
    item = Item()
    for childnode in node.childNodes:
      # if a data element
      if childnode.nodeName == 'data':
        name = childnode.getAttribute('name')
        #if not name in [ 'id', 'parentid' ]: # don't overwrite the id or parentid!
        value = ''
        for grandchild in childnode.childNodes:
          if grandchild.nodeType == xml.dom.Node.CDATA_SECTION_NODE:
            value = pickle.loads(str(grandchild.nodeValue))
            break
        setattr(item, name, value)
      
      # if a child element
      elif childnode.nodeName == 'child':
        # create the new child
        child = _import_xml(childnode)
        # update its parentid and my childid list
        child.parentid = item.id
        item.childids.append(child.id)
        # put in the items_cache since we'll need to get to it again
        items_cache[child.id] = [ threading.RLock(), child ]
    return item
  
  finally:
    items_lock.release()
    
    
def import_xml(root):
  '''Imports an xml document (starting with some root node) into a set of items that 
     were exported via item.export().  The root node should have one child named "items"
     that is the parent element of all items in the import.
     This method does NOT save the items.  It just creates them in memory.
     The new items are not linked into the main items tree.
  '''
  items_lock.acquire()
  try:
    # drop to the "items" node, since that is where the items start
    for child in root.childNodes:
      if child.nodeName == 'items':
        itemsnode = child
        break
    else:
      raise 'Could not find the "items" child in the import document.'
  
    # import the items
    import traceback
    try:
      return _import_xml(itemsnode)
    except:
      traceback.print_exc()
    
  finally:
    items_lock.release()
    
    
