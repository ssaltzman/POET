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
import datagate
import sys
import StringIO
import time


############################################################
###  Field classes to represent different field types

MONTHS = [ '', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December' ]

class Field:
  '''Base class of all fields'''
  def __init__(self, name):
    self.name = name

  def add_form_params(self, params):
    params['custom' + self.name] = None

  def save_info(self, request, activity):
    '''Saves information into the activity object for this field.  Doesn *not* save() the activity. '''
    setattr(activity, 'custom' + self.name, request.getvalue('custom' + self.name, ''))
    

class TextField(Field):
  '''A text field'''
  class_name = "TextField"
  
  def __init__(self, name, params):
    Field.__init__(self, name)
    self.rows, self.cols = [ int(param) for param in params ] # convert to integers
    
  def get_form_html(self, activity):
    if self.rows <= 1:
      return '<input name="custom' + self.name + '" type="text" size="' + str(self.cols) + '" value="' + activity.getvalue('custom' + self.name, '') + '">'
    else:
      return '<textarea name="custom' + self.name + '" rows="' + str(self.rows) + '" cols="' + str(self.cols) + '">' + activity.getvalue('custom' + self.name, '') + '</textarea>'
    
    
    
def get_time(name, activity):
  '''Convenience method to return the time (in seconds since epoch) stored in the 
     activity for the date field by this name.
  '''
  month, day, year = get_date(name, activity)
  return time.mktime( (year, month, day, 0, 0, 0, 0, 0, 0 ) )
    
    
def get_date(name, activity):
  '''Convenience method to return a tuple of month, day, year stored in the activity for the date field by this name'''
  if activity:
    return int(activity.getvalue('custom' + name + '-month', time.strftime('%m'))), \
           int(activity.getvalue('custom' + name + '-day', time.strftime('%d'))), \
           int(activity.getvalue('custom' + name + '-year', time.strftime('%Y')))
  else: 
    return int(time.strftime('%m')), int(time.strftime('%d')), int(time.strftime('%Y'))
    
class DateField(Field):
  '''A date field'''
  class_name = "DateField"
  
  def save_info(self, request, activity):
    '''Saves information into the activity object for this field.  Doesn *not* save() the activity. '''
    month, day, year = get_date(self.name, request) 
    setattr(activity, 'custom' + self.name + '-month',  str(month))
    setattr(activity, 'custom' + self.name + '-day', str(day))
    setattr(activity, 'custom' + self.name + '-year', str(year))
    
  def add_form_params(self, params):
    params['custom' + self.name + '-month'] = None
    params['custom' + self.name + '-day'] = None
    params['custom' + self.name + '-year'] = None
    
  def get_form_html(self, activity):
    buffer = ''
    # the month
    month, day, year = get_date(self.name, activity)
    buffer += '<select name="custom' + self.name + '-month">'
    for i in range(1, len(MONTHS)):
      buffer += '<option value="' + str(i) + '"'
      if i == month:
        buffer += ' selected'
      buffer += '>' + MONTHS[i] + '</option>'
    buffer += '</select>'
    buffer += ' '
    # the day
    buffer += '<select name="custom' + self.name + '-day">'
    for i in range(1, 32):
      buffer += '<option value="' + str(i) + '"'
      if i == day:
        buffer += ' selected'
      buffer += '>' + str(i) + '</option>'
    buffer += '</select>'
    buffer += ' '
    # the year
    buffer += '<input name="custom' + self.name + '-year" size="8" maxlength="4" value="' + str(year) + '">'
    return buffer
    
    
class CheckboxField(Field):
  '''A checkbox field'''
  class_name = "CheckboxField"
  
  def save_info(self, request, activity):
    '''Saves information into the activity object for this field.  Doesn *not* save() the activity. '''
    if request.getvalue('custom' + self.name, '0') == '1':
      setattr(activity, 'custom' + self.name, '1')
    else:
      setattr(activity, 'custom' + self.name, '0')

  def get_form_html(self, activity):
    checked = ''
    if activity.getvalue('custom' + self.name, '0') == '1':
      checked = ' checked'
    return '<input name="custom' + self.name + '" type="checkbox" value="1" ' + checked + '>'


class SelectField(Field):
  '''A selection box field'''
  class_name = "SelectField"
  
  def __init__(self, name, params):
    Field.__init__(self, name)
    self.rows = int(params[0])
    self.values = []
    for i in range(1, len(params) - 1, 2):
      self.values.append( (params[i], params[i+1]) )
          
  def get_form_html(self, activity):
    st = '<select name="custom' + self.name + '" size="' + str(self.rows) + '">'
    current = activity.getvalue('custom' + self.name, '')
    for value in self.values:
      st += '<option'
      if value[0] == current:
        st += ' selected'
      st += ' value="' + value[0] + '">' + value[1] + '</option>'
    st += '</select>'
    return st
    

field_types = { 'TEXT': TextField, 'DATE': DateField, 'CHECKBOX': CheckboxField, 'SELECT': SelectField }

def get_fields(fields_text):
  '''Parses the fields and returns a list of field objects (TextField, DateField, etc.).
     Throws an error if the format is wrong.  This is a factory method to create field objects.
  '''
  fields = []
  for line in StringIO.StringIO(fields_text).readlines():
    line = line.strip()
    if line == '': # skip empty lines
      continue
    try:
      spacepos = line.find(' ')
      fieldtype, name = line[0: spacepos], line[spacepos + 1: ]
      paren1 = fieldtype.find('(')
      paren2 = fieldtype.find(')')
      if paren1 >= 0: # has parameters
        obj_type = fieldtype[0: paren1]
        params = fieldtype[paren1 + 1: paren2].split(',')
        params = [ decode(param) for param in params ]
        field_obj = field_types[obj_type.upper()](name, params)

      else: # no parameters
        field_obj = field_types[fieldtype.upper()](name)

      fields.append(field_obj)
    except:
      import traceback
      traceback.print_exc()
      raise 'Error on line: ' + line
  return fields
  
  
  
  
#######################################
###   Main view class


class CustomField(BaseView):
  '''A custom field view.  Admins can define text and select fields that show on the 
     custom view.  All users share the same values for the fields.
     
     The view is not interactive since it is not expected that changes are made often.
  '''
  NAME = 'Custom Field'
  rights_list = [ 'View', 'Edit' ]
  
  def __init__(self):
      BaseView.__init__(self)
     

  def send_content(self, request):
    '''Sends the view to the client'''
    activity = datagate.get_item(request.getvalue('global_rootid', ''))
    rights = self.get_user_rights(request)
    
    if not rights['View']:
      request.writeln(HTML_HEAD + HTML_BODY + '<center>You do not have rights to view this pane.<p>Please see your administrator for additional help.</center></body></html>')  
      return
    
    try:
      # are we within a tree or by ourselves?
      if hasattr(activity, 'linkitemid'):
        linkitem = datagate.get_item(activity.linkitemid)
        title = linkitem.getvalue('title', '')
        fields = get_fields(linkitem.customfields)
        
      else:
        title = activity.getvalue('title', '')
        fields = get_fields(activity.customfields)

    except:
      request.writeln(HTML_HEAD + HTML_BODY)
      request.writeln('Error: The administrator has not set up this activity correctly.')
      request.writeln('<p>')
      request.writeln('More info: <tt>' + str(sys.exc_info()[0]) + '</tt>')
      request.writeln('</body></html>')
      return

    # save any changes from last time
    request.writeln(HTML_HEAD + HTML_BODY)
    action = request.getvalue('action', '')
    if action == 'savefields':
      try:
        for field in fields:
          field.save_info(request, activity)
        activity.save()
        request.writeln('<p align="center"><font color="red">Changes saved</font></p>')
      except:
        activity.load()  # reset the activity
        request.writeln('<p align="center"><font color="red">Error saving changes.  Did you enter an incorrect year?</font></p>')
    
    # send the html
    request.writeln('<center>')
    if title != '':
      request.writeln('<p><b>' + title + '</b></p>')
    formparams = { 'action': 'savefields' }
    for field in fields:
      field.add_form_params(formparams)
    if rights['Edit']:
      request.writeln(request.cgi_form(**formparams))
    request.writeln('<table border=1 cellspacing=0 cellpadding=5>')
    for field in fields:
      request.writeln('<tr>')
      request.writeln('<td valign="top"><b>' + field.name + '</b>:</td>')
      request.writeln('<td valign="top">')
      request.writeln(field.get_form_html(activity))
      request.writeln('</td>');
      request.writeln('</tr>')
    request.writeln('</table>')
    if rights['Edit']:
      request.writeln('<p><input type=submit value="Save Changes"></p>')
      request.writeln('</form>')
    request.writeln('</center>')
    request.writeln('</body></html>')
  
  
  
  def send_admin_page(self, request):
    '''Sends an administrator page for this view.'''
    activity = datagate.get_item(request.getvalue('itemid', ''))
    
    # send the rights
    request.writeln('<center>')
    self.send_admin_rights(request, activity)
    request.writeln('</center><p>&nbsp;<p>')
    
    # send the html      
    request.writeln(request.cgi_form(gm_action='CustomField.savechanges', title=None, fields=None) + '''
      <center>
      <b>View Title:</b>
      <input type=text size=40 name=title value="''' + activity.getvalue('title', '') + '''">
      <p>
      <b>Field Definitions:</b>
      <p>
      Provide one row per field.  Each row should be formatted as follows: <tt>type name</tt> (separated by spaces).
      <p>
      <textarea name="fields" cols=50 rows=15>''' + activity.getvalue('customfields', '') + '''</textarea>
      <p>
      <input type=submit value="Save">
      </form>
      <p>
      (Valid types are <tt>TEXT(rows,cols)</tt>, <tt>CHECKBOX</tt>, <tt>DATE</tt>, and <tt>SELECT(rows,id1,value1,id2,value2,...)</tt>)
      </center>
   ''')


  
  def savechanges_action(self, request):
    activity = datagate.get_item(request.getvalue('itemid', ''))
    request.writeln('<p align="center"><font color="red">Changes saved</font></p>')
    activity.customfields = request.getvalue('fields', '')
    try: # do a little data checking
      get_fields(activity.customfields)
    except:        
      request.writeln('''<p align="center"><font color="red">Warning: ''' + sys.exc_info()[0] + '''</font></p>''')
    activity.title = request.getvalue('title', '')
    activity.save()
      
