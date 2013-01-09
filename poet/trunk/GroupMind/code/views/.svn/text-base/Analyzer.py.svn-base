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
import Directory
import datagate

TREE_WIDTHS = [
  ( '10%', 'Tree 10% / Tabs 90%' ),
  ( '20%', 'Tree 20% / Tabs 80%' ),
  ( '30%', 'Tree 30% / Tabs 70%' ),
  ( '40%', 'Tree 40% / Tabs 60%' ),
  ( '50%', 'Tree 50% / Tabs 50%' ),
  ( '60%', 'Tree 60% / Tabs 40%' ),
  ( '70%', 'Tree 70% / Tabs 30%' ),
  ( '80%', 'Tree 80% / Tabs 20%' ),
  ( '90%', 'Tree 90% / Tabs 10%' ),
]

class Analyzer(BaseView.BaseView):
  NAME = 'Analyzer'
      
  def initialize_activity(self, request, new_activity):
    '''Called from the Administrator.  Sets up the activity'''
    # set up the tree root
    treeroot = datagate.create_item(creatorid=request.session.user.id, parentid=new_activity.id)
    treeroot.type = 'TreeRoot'
    treeroot.save()
    
    # set up the tree links node
    treelinks = datagate.create_item(creatorid=request.session.user.id, parentid=new_activity.id)
    treelinks.type = 'TreeLinks'
    treelinks.save()

    # let the tree initialize itself      
    BaseView.views['tree'].initialize_activity(request, treeroot, treelinks)

    # set up the tabs for this activity
    tabdefs = datagate.create_item(creatorid=request.session.user.id, parentid=new_activity.id)
    tabdefs.type = 'TabDefs'
    tabdefs.name = 'Activity Tabs'
    tabdefs.save()
    BaseView.views['tabpane'].initialize_activity(request, tabdefs)

      
  def send_content(self, request):
    # get the activity
    root = datagate.get_item(request.getvalue('global_rootid', ''))

    # get the tree root node
    treeroot = root.search1(type='TreeRoot')
    
    # get the tree links node
    treelinks = root.search1(type='TreeLinks')
    
    # get the tab definitions (define the tabs to be shown)
    tabdefs = root.search1(type='TabDefs')
    
    # send the frames
    request.writeln(HTML_HEAD)
    request.writeln("<frameset border='1' cols='" + root.getvalue('treewidth', '30%') + ",*'>")
    request.writeln("<frame marginheight='0' marginwidth='0' name='tree' src='" + request.cgi_href(global_rootid=treeroot.id, view='Tree', tabdefsid=tabdefs.id, target='tabpane', linkview='TabPane', treelinkid=treelinks.id) + "'>")
    request.writeln("<frame marginheight='0' marginwidth='0' name='tabpane' src='" + request.cgi_href(view='Blank') + "'>")
    request.writeln("</frameset>")
    request.writeln("</html>")    
    
    
    
  ################################################
  ###   Administrator functions for the view
    
  def send_admin_page(self, request):
    '''Called from the administrator to allows customization of the activity'''
    activity = datagate.get_item(request.getvalue('itemid', ''))
    treewidth = activity.getvalue('treewidth', '')

    # show my admin part of the page
    request.writeln('''
      <p><center><font size=+1>
      Edit GroupMind Activity: ''' + activity.name + '''
      </font></center></p>
    ''')
    
    # tree/pane width
    request.writeln('''
      <center>
      ''' + request.cgi_form(gm_action='Analyzer.savewidth', treewidth=None) + '''
      Screen Layout: <select name="treewidth">
    ''')
    for width, name in TREE_WIDTHS:
      request.write('<option value="' + width + '"')
      if width == treewidth:
        request.write(' selected')
      request.writeln('>' + name + '</option>')
    request.writeln('''
      </select>
      <input type=submit value="Save">
      </form>
      </center>
      <p>&nbsp;<p>
    ''')
    
    # get the tree root node
    treeroot = activity.search1(type='TreeRoot')
    request.writeln('''
      <center>
      <a href="''' + request.cgi_href(itemid=treeroot.id, global_adminview='tree') + '''">Edit Tree Options</a>
      </center>
      <p>
    ''')    
    
    
    # I have to pop the tabs out because the TabsDef windows expects itemid to be the TabDefs item
    # rather than the activity (GroupMind) item.  I am able to work it through once, but not
    # through all the activity in the TabPane administrator (edit, delete, up, down, add, etc.)
    tabdefs = activity.search1(type='TabDefs')
    request.writeln('''
      <center>
      <a href="''' + request.cgi_href(itemid=tabdefs.id, global_adminview='tabpane') + '''">Edit Tabs Names and Types</a>
      </center>
      <p>
    ''')    
    

  def savewidth_action(self, request):
    activity = datagate.get_item(request.getvalue('itemid', ''))
    activity.treewidth = request.getvalue('treewidth', '')
    activity.save()
