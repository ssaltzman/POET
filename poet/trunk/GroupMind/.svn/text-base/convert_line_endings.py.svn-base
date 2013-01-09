#!/usr/bin/python

'''
Converts line endings in all the files to Unix type.  Looks for DOS and Mac endings
and translates them.
'''

import os, os.path, sys

# does the actual translation for a file
def translate(filename):
  # open the file in binary mode
  f = open(filename, 'rb')
  text = f.read()
  f.close()
  
  # translate all the lines
  text = text.replace('\r\n', '\n')  # windows (must come before mac or we get \n\n)
  text = text.replace('\r', '\n')    # mac
  
  # translate any tab characters to two spaces
  text = text.replace('\t', '  ')
  
  # save back out
  f = open(filename, 'wb')
  f.write(text)
  f.close()
  

# walk through the dirs and find python files
for root, dirs, files in os.walk('./code'):
  for filename in files:
    fullname = os.path.join(root, filename)
    name, ext = os.path.splitext(filename)
    if ext == '.py':
      print 'Translating', fullname
      translate(fullname)
