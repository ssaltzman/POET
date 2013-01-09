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

import BaseView
from Constants import *
import datagate
from views import TabPane
from views import MeetingHome

class GridView(BaseView.BaseView):
  NAME = 'GridView'


  def send_content(self, request):
    '''Sends the main content for this view'''
    # get the activity
    activity = datagate.get_item(request.getvalue('global_rootid', ''))

    numrows = activity.getvalue('rows', 1)
    rows = [ str(int(100.0 / float(numrows))) + "%" for i in range(numrows)]
    numcols = activity.getvalue('cols', 1)
    cols = [ str(int(100.0 / float(numcols))) + "%" for i in range(numcols)]
    
    # send the frames
    request.writeln(HTML_HEAD)
    request.writeln('<frameset border="1" rows="' + ','.join(rows) + '">')
    for row in range(1, numrows + 1):
      request.writeln('<frameset border="1" cols="' + ','.join(cols) + '">')
      for col in range(1, numcols + 1):
        child = self.getview(request, activity, row, col)
        request.writeln('<frame marginheight="0" marginwidth="0" src="' + request.cgi_href(view=child.view, global_rootid=child.id) + '">')
      request.writeln('</frameset>')
    request.writeln('</frameset>')
    request.writeln('</html>')    
    
    
  def getview(self, request, activity, row, col, default_view='blank'):
    '''Returns the view at the specified position, creating it if necessary'''
    index = 'row' + str(row) + 'col' + str(col)
    child = activity.search1(position=index)
    if child == None:
      child = datagate.create_item(creatorid=request.session.user.id, parentid=activity.id)
      child.position = index
      child.view = default_view
      child.save()
      BaseView.views[child.view].initialize_activity(request, child)
    return child
  
    
  ################################################
  ###   Administrator functions for the view
    
  def initialize_activity(self, request, new_activity):
    '''Called from the Administrator.  Sets up the activity.'''
    # create the initial child
    self.getview(request, new_activity, 1, 1)
    
    
  def send_admin_page(self, request):
    '''Called from the administrator to allows customization of the activity'''
    activity = datagate.get_item(request.getvalue('itemid', ''))

    # the change form
    request.writeln('<center>')
    request.writeln(request.cgi_form(gm_action="GridView.rowscols", Rows=None, Columns=None, itemid=request.getvalue('itemid', '')))
    request.writeln('<b>Grid Size</b>:')
    request.writeln('<table border=0>');
    for axis, val in [ ('Rows', activity.getvalue('rows', 1)), ('Columns', activity.getvalue('cols', 1)) ]:    
      request.writeln('<tr>')
      request.writeln('<td>' + axis + ':</td>')
      request.writeln('<td><select name="' + axis + '" onchange="javascript:form.submit()">')
      for i in range(1, 11):
        request.write('<option')
        if i == val:
          request.write(' selected')
        request.writeln('>' + str(i) + '</option>')
      request.writeln('</select></td>')  
      request.writeln('</tr>')
    request.writeln('</table>')
    request.writeln('</form>')
    
    # display the grid for the subviews
    request.writeln('<p>&nbsp;</p>')
    request.writeln('<b>Grid View Types</b>')
    request.writeln('<table border=1 cellspacing=0 cellpadding=2>')
    for row in range(1, activity.getvalue('rows', 1) + 1):
      request.writeln('<tr>')
      for col in range(1, activity.getvalue('cols', 1) + 1):
        child = self.getview(request, activity, row, col)
        request.writeln('<td>')
        request.writeln(request.cgi_form(gm_action="GridView.changeview", childview=None, row=row, col=col, itemid=request.getvalue('itemid', '')))
        request.writeln('<select name="childview" onchange="javascript:form.submit()">')
        for view in MeetingHome.meeting_components:
          comp = BaseView.get_view(view)
          request.write('<option')
          if view == child.view:
            request.writeln(' selected')
          request.writeln(' value="' + view + '">' + comp.NAME + '</option>')
        request.writeln('</select>')
        request.writeln('<br>')
        request.write('<center><font size="1">[ <a href="' + request.cgi_href(itemid=child.id, gm_action=None, view='Administrator', global_adminview=child.view) + '">Edit</a> ]</font></center>')
        request.writeln('</form>')
        request.writeln('</td>')
      request.writeln('</tr>')
    request.writeln('</table>')
    
    # footer
    request.writeln('<p><i>(Changes are saved automatically)</i><p>')
    request.writeln('</center>')
    
    
  def rowscols_action(self,request):
    activity = datagate.get_item(request.getvalue('itemid', ''))
    # save the number of rows and cols
    activity.rows = int(request.getvalue('Rows', 1))
    activity.cols = int(request.getvalue('Columns', 1))
    activity.save()
    
    # ensure a default component exists for each position
    for row in range(1, activity.rows + 1):
      for col in range(1, activity.cols + 1):
        self.getview(request, activity, row, col) # getview creates if necessary
    
  def changeview_action(self, request):
    activity = datagate.get_item(request.getvalue('itemid', ''))
    # delete this child if it exists
    child = self.getview(request, activity, request.getvalue('row', '1'), request.getvalue('col', '1'))
    child.delete()
    # now recreate it
    child = self.getview(request, activity, request.getvalue('row', '1'), request.getvalue('col', '1'), request.getvalue('childview', 'blank'))
    child.name = child.view
    child.save()
    
  
