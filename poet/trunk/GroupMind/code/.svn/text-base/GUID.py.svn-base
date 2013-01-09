#!/usr/bin/env python

# GUID.py
# Version 2.7
#
# Copyright (c) 2006 Conan C. Albrecht
#
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is furnished 
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

__doc__ = '''
  A globally-unique identifier made up of time and ip and 8 digits for a counter: 
  each GUID is 40 characters wide.

  A globally unique identifier that combines ip, time, and a counter.  Since the 
  time is listed first, you can sort records by guid.  You can also extract the time 
  and ip if needed.  

  Since the counter has eight hex characters, you can create up to 
  0xffffffff (4294967295) GUIDs every millisecond.  If your processor
  is somehow fast enough to create more than that in a millisecond (looking
  toward the future, of course), the function will wait until the next
  millisecond to return.
     
  GUIDs make wonderful database keys.  They require no access to the 
  database (to get the max index number), they are extremely unique, and they sort 
  automatically by time.   GUIDs prevent key clashes when merging
  two databases together, combining data, or generating keys in distributed
  systems.
  
  GUIDs are always returned as strings.  I did not make this a "real" class because
  it just complicates things.  Since GUIDs are generally stored in databases, sockets,
  and elsewhere as strings, I prefer to just keep them always as strings.  In other
  words, I don't see much benefit in having GUID objects over regular string objects.
  
  There is an Internet Draft for UUIDs, but this module does not implement it.
  If the draft catches on, perhaps I'll conform the module to it.
'''

# Changelog
# Sometime, 1997     Created the Java version of GUID
#                    Went through many versions in Java
# Sometime, 2002     Created the Python version of GUID, mirroring the Java version
# November 24, 2003  Changed Python version to be more pythonic, took out object and made just a module
# December 2, 2003   Fixed duplicating GUIDs.  Sometimes they duplicate if multiples are created
#                    in the same millisecond (it checks the last 100 GUIDs now and has a larger random part)
# December 9, 2003   Fixed MAX_RANDOM, which was going over sys.maxint
# June 12, 2004      Allowed a custom IP address to be sent in rather than always using the 
#                    local IP address.  
# November 4, 2005   Changed the random part to a counter variable.  Now GUIDs are totally 
#                    unique and more efficient, as long as they are created by only
#                    on runtime on a given machine.  The counter part is after the time
#                    part so it sorts correctly.
# November 8, 2005   The counter variable now starts at a random long now and cycles
#                    around.  This is in case two guids are created on the same
#                    machine at the same millisecond (by different processes).  Even though
#                    it is possible the GUID can be created, this makes it highly unlikely
#                    since the counter will likely be different.
# November 11, 2005  Fixed a bug in the new IP getting algorithm.  Also, use IPv6 range
#                    for IP when we make it up (when it's no accessible)
# November 21, 2005  Added better IP-finding code.  It finds IP address better now.
# January 5, 2006    Fixed a small bug caused in old versions of python (random module use)
# January 7, 2006    Reformatted the documentation to epydoc format


import math
import socket
import random
import sys
import time
import threading



#############################
###   global module variables

#Makes a hex IP from a decimal dot-separated ip (eg: 127.0.0.1)
make_hexip = lambda ip: ''.join(["%04x" % long(i) for i in ip.split('.')]) # leave space for ip v6 (65K in each sub)
  
MAX_COUNTER = 0xfffffffe
counter = 0L
firstcounter = MAX_COUNTER
lasttime = 0
ip = ''
lock = threading.RLock()
try:  # only need to get the IP addresss once
  ip = socket.getaddrinfo(socket.gethostname(),0)[-1][-1][0]
  hexip = make_hexip(ip)
except: # if we don't have an ip, default to someting in the 10.x.x.x private range
  ip = '10'
  rand = random.Random()
  for i in range(3):
    ip += '.' + str(rand.randrange(1, 0xffff))  # might as well use IPv6 range if we're making it up
  hexip = make_hexip(ip)

  
#################################
###   Public module functions

def generate(ip=None):
  '''Generates a new guid.  This is the primary method of the module.
     A guid is unique in space and time because it combines
     the machine IP with the current time in milliseconds.  It also includes
     a counter to provide uniqueness if two GUIDs are created in a single millisecond.
     
     Be careful about sending in
     a specified IP address because the ip makes it unique in space.  You could send in
     the same IP address that is created on another machine.  You should generally leave this
     parameter at its default value of None.
     
     @param ip: The IP address to use for this GUID.  Defaults to the machine IP as returned by socket.getaddrinfo().  Normally this parameter should be left as None.
     @type  ip: str
     @returns:  A new GUID.
     @rtype:    str
  '''
  global counter, firstcounter, lasttime
  lock.acquire() # can't generate two guids at the same time
  try:
    parts = []

    # do we need to wait for the next millisecond (are we out of counters?)
    now = long(time.time() * 1000)
    while lasttime == now and counter == firstcounter: 
      time.sleep(.01)
      now = long(time.time() * 1000)

    # time part
    parts.append("%016x" % now)

    # counter part
    if lasttime != now:  # time to start counter over since we have a different millisecond
      firstcounter = long(random.uniform(1, MAX_COUNTER))  # start at random position
      counter = firstcounter
    counter += 1
    if counter > MAX_COUNTER:
      counter = 0
    lasttime = now
    parts.append("%08x" % (counter)) 

    # ip part
    parts.append(hexip)

    # put them all together
    return ''.join(parts)
  finally:
    lock.release()
    

def extract_time(guid):
  '''Extracts the time portion out of the guid and returns the 
     number of seconds since the epoch as a float.
  
     @param guid: The guid to extract the time from.
     @type  guid: str
     @returns:    The time this GUID was created as the number of seconds since the epoch (see the standard time module for more info).
     @rtype:      float
  '''
  return float(long(guid[0:16], 16)) / 1000.0


def extract_counter(guid):
  '''Extracts the counter from the guid.  Each GUID has a counter
     that ensures the GUID is unique, even if two GUIDs are created
     on the same comptuer at the same millisecond.  The counter is
     started at a random place in the range of an integer, so
     it's value is generally meaningless. :)
     
     @param guid: The guid to extract the counter from.
     @type  guid: str
     @returns:    The counter used when this GUID was created.
     @rtype:      int
  '''
  return int(guid[16:24], 16)


def extract_ip(guid):
  '''Extracts the ip portion out of the guid and returns it
     as a string like 10.10.10.10.  This generally provides 
     the machine IP where the GUID was created (unless the IP
     could not be determined at creation time).
     
     @param guid: The guid to extract the counter from.
     @type  guid: str
     @returns:    The IP address as something like "10.10.10.10".
     @rtype:      str
  '''
  # there's probably a more elegant way to do this
  thisip = []
  for index in range(24, 40, 4):
    thisip.append(str(int(guid[index: index + 4], 16)))
  return '.'.join(thisip)



### TESTING OF GUID CLASS ###
if __name__ == "__main__":
  guids = []
  for i in range(10):  # calculate very fast so people can see the counter in action
    guid = generate()
    guids.append(guid)
  for guid in guids:
    print "GUID:", guid
    guidtime = extract_time(guid)
    print "\tTime:   ", time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime(guidtime)), '(millis: ' + str(round(guidtime - long(guidtime), 3)) + ')'
    print "\tIP:     ", extract_ip(guid)
    print "\tCounter:", extract_counter(guid)
  

  