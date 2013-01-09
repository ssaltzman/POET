#!/usr/bin/python


#     TimedDict: A dictionary that times elements out automatically
#     Copyright (C) 2003  Conan C. Albrecht
# 
#     This library is free software; you can redistribute it and/or
#     modify it under the terms of the GNU Lesser General Public
#     License as published by the Free Software Foundation; either
#     version 2.1 of the License, or (at your option) any later version.
# 
#     This library is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#     Lesser General Public License for more details.
# 
#     You should have received a copy of the GNU Lesser General Public
#     License along with this library; if not, write to the Free Software
#     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys
import threading
import time

class TimedDict(dict):
  '''A simple extension to the standard Python dict data type to allow for 
     automatic, timed removal of unused elements.  Defaults to 30 minute timeout.
     The listener var is a callable function that will be called just before items
     are removed with listener(key, value). 
  '''
  def __init__(self, timeout_in_seconds=1800, listener=None):
    self.timeout = timeout_in_seconds
    self.listener = listener
    self.lock = threading.RLock()
    self.access_times = {}
    self.thread = threading.Thread(target=self.run)
    self.thread.setDaemon(1)
    self.thread.start()
    
  def __del__(self):
    self.running = 0
  
  ###############################
  ###   Overriding dict methods
  
  def __getitem__(self, key):
    self.lock.acquire()
    try:
      value = dict.__getitem__(self, key)
      self.access_times[key] = time.time()
      return value
    finally:
      self.lock.release()
      
  def __setitem__(self, key, value):
    self.lock.acquire()
    try:
      dict.__setitem__(self, key, value)
      self.access_times[key] = time.time()
    finally:
      self.lock.release()
  
  def __delitem__(self, key):
    self.lock.acquire()
    try:
      if self.has_key(key):
        if self.listener != None:
          self.listener(key, dict.__getitem__(self, key))
        dict.__delitem__(self, key)
        del self.access_times[key]
    finally:
      self.lock.release()
      
      
  def getvalue(self, key, default):
    '''Convenience method to retrieve a value if it exists, or return a default value'''
    if self.has_key(key):
      return self[key]
    return default
    
    
  ###################################
  ###   Thread to check for old items
    
  def run(self):
    e = threading.Event()
    self.running = 1
    while self.running:
      try:
        # wait for a bit
        e.wait(self.timeout / 2)
        
        # check for old items
        self.lock.acquire()
        try:
          old = time.time() - self.timeout
          for key in self.access_times.keys():
            if self.access_times[key] < old:
              self.__delitem__(key)
        finally:
          self.lock.release()
      except:
        pass 
          
    
###############################
###   Debugging

if __name__ == '__main__':
  d = TimedDict(5)
  d['a'] = 1
  d['b'] = 2
  e = threading.Event()
  while len(d) > 0:
    print d
    e.wait(2)
  print d