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

# to do:
# 1. DONE Only show after final revision
# 2. Make rating be a right

from Events import Event
from Commenter import Commenter
from Constants import *
import datagate, threading

class CommenterReviser(Commenter):
  NAME = 'Commenter with Revisions'
  INPUT_WINDOW_HEIGHT = "125"
  
  def __init__(self):
    Commenter.__init__(self)
    self.lock = threading.RLock()
    

  def send_input(self, request):
    '''Overrides send_input in commenter to send either the add window or the revise window'''
    self.lock.acquire()
    try:
      root = datagate.get_item(request.getvalue('global_rootid', ''))

      # go through and find all comments that this user could revise
      revisable_comments = []
      user = request.session.user
      root = datagate.get_item(request.getvalue('global_rootid', ''))
      comments = root.search1(name="comments")
      myrevisingcomment = None 
      num_comments_needing_revising = 0
      for comment in comments:
        # add to the total number of comments needing revising
        if len(comment.versions) <= root.num_comment_revisions and comment.bestrevision == None:
          num_comments_needing_revising += 1
        
        # was I already assigned to revise this comment?
        if comment.revisingnow == user.id:  # just in case user crashed when revising -- give the same one back to them (no closing and coming back so you can skip one!!!)
          myrevisingcomment = comment
          break
          
        # can I revise this comment?
        elif len(comment.versions) <= root.num_comment_revisions and comment.bestrevision == None and comment.revisingnow == None and not user.id in comment.authors:
          revisable_comments.append(comment)
          
      # sort the comments first by the number of revisions, then by time of creation
      revisable_comments.sort(lambda a,b: cmp(len(a.versions), len(b.versions)) or cmp(a.id, b.id))
          
      # if the number of comments this user can revise is greater than the number we're OK with not revising, let them revise it
      if not myrevisingcomment and len(revisable_comments) > 0 and num_comments_needing_revising > root.min_unrevised:
        myrevisingcomment = revisable_comments[0]
      if myrevisingcomment:
        myrevisingcomment.revisingnow = user.id
        myrevisingcomment.save()
        if len(myrevisingcomment.versions) == root.num_comment_revisions:  # ready for best one to be picked
          self.send_pickbestform(request, myrevisingcomment.id)
        else:  # needs another revision
          self.send_reviseform(request, myrevisingcomment.id)
      else:
        self.send_input_super(request)
    finally:
      self.lock.release()
      
  
  def send_input_super(self, request):
    '''This is an almost exact copy of Commenter.send_input, with a slight change for the additional information'''
    rights = self.get_user_rights(request)
    request.writeln(
      HTML_HEAD + self.BODY_TAG_NO_CLOSE + ''' topmargin="8"><center>
    ''')
    
    if rights['Add']: # add right
      request.writeln(request.cgi_form(subview='send_input', reload='yes', gm_action="add_comment") + '''
        <div align="center"><textarea name="text" cols="50" rows="2" style="width:80%"></textarea></div>
        <div align="center"><input type="submit" value="Add" name="submit"></div>
        </form>
      ''')
      self.send_queue_info(request)
      if request.getvalue('reload', '') == 'yes': # this comes from send_editform below
        request.writeln("<script language='JavaScript' type='text/javascript'>parent.refreshEvents();</script>")
      request.writeln('''
        </body>
        </html>
      ''')    
    

  def send_reviseform(self, request, itemid):
    '''Sends the revise comment form'''
    item = datagate.get_item(itemid)
    request.writeln(
      HTML_HEAD + self.BODY_TAG_NO_CLOSE + ''' topmargin="8">
      ''' + request.cgi_form(subview='send_input', reload='yes', gm_action="revise_comment", itemid=item.id) + '''
      <center>
      <table border=0 cellspacing=0 cellpadding=2>
        <tr>
          <td valign="top">Please revise this comment:</td>
          <td valign="top"><b>''' + item.text + '''</b>
          <td valign="top">&nbsp;</td>
        </tr><tr>
          <td valign="top">&nbsp;</td>
          <td valign="top"><textarea name="text" cols="70" rows="2"></textarea>
          <td valign="top"><input type="submit" value="Submit"></td>
        </tr>
      </table>
      </center>
      </form>
    ''')
    self.send_queue_info(request)
    if request.getvalue('reload', '') == 'yes': # this comes from send_editform below
      request.writeln("<script language='JavaScript' type='text/javascript'>parent.refreshEvents();</script>")
    request.writeln('</body></html>')
  
  
  def send_pickbestform(self, request, itemid):
    '''Sends the revise comment form'''
    item = datagate.get_item(itemid)
    request.writeln(
      HTML_HEAD + self.BODY_TAG_NO_CLOSE + ''' topmargin="8">
      ''' + request.cgi_form(subview='send_input', reload='yes', gm_action="pickbestrevision", itemid=item.id) + '''
      <center>
      
      <table border=0 cellspacing=5 cellpadding=0>
        <tr>
          <td valign="top">Please pick the best version of this comment:</td>
          <td valign="top">
            <table border=0 cellspacing=2 cellpadding=0>
    ''')
    for i, version in enumerate(item.versions):
      request.writeln('<tr>')
      request.writeln('<td><input type="radio" name="bestone" value="' + str(i) + '"></td>')
      request.writeln('<td>' + str(i+1) + '. ' + version + '</td>')
      request.writeln('</tr>')
    request.writeln('''
            </table>
          </td>
          <td valign="top"><input type="submit" value="Submit"></td>
        </tr>
      </table>
      </center>
      </form>
    ''')
    self.send_queue_info(request)
    if request.getvalue('reload', '') == 'yes': # this comes from send_editform below
      request.writeln("<script language='JavaScript' type='text/javascript'>parent.refreshEvents();</script>")
    request.writeln('</body></html>')
  
  
  def send_queue_info(self, request):
    '''Sends a short snippet about queue information to the client'''
    root = datagate.get_item(request.getvalue('global_rootid', ''))
    comments = root.search1(name="comments")
    num_in_revision = 0
    for comment in comments:
      if comment.creatorid == request.session.user.id and comment.bestrevision == None:
        num_in_revision += 1
    request.writeln('<div align="right">You have ' + str(num_in_revision) + ' comment' + (num_in_revision != 1 and 's' or '') + ' in the revision queue&nbsp;&nbsp;&nbsp;</div>')
    
    
  
  ###############################################
  ###   Actions
  

  def get_initial_events(self, request, rootid):
    '''Retrieves a list of initial javascript calls that should be sent to the client
       when the view first loads.  Typically, this is a series of add_processor
       events.'''
    events = []
    root = datagate.get_item(rootid)
    comments = root.search1(name="comments")
    for item in comments.get_child_items():
      if item.bestrevision != None:
        events.append(self._create_add_event(item))
    return events


  def pickbestrevision_action(self, request):
    '''Picks the best revision of a comment'''
    self.lock.acquire()
    try:
      item = datagate.get_item(request.getvalue('itemid', ''))
      bestone = int(request.getvalue('bestone'))
      author = request.session.user
      
      # update the tree
      item.bestrevision = bestone
      item.bestrevisionauthor = author
      item.revisingnow = None  # so others can now revise this item
      item.text = item.versions[bestone]  # this allows the regular commenter to update the view
      item.save()
      
      # send the add event (finally sends the node to the output screen)
      return self._create_add_event(item)
     
    finally:
      self.lock.release()
    
  
  def add_comment_action(self, request):
    '''Responds to an add from the browser.'''
    self.lock.acquire()
    try:
      # create the new item 
      text = request.getvalue('text', '')
      creator = request.session.user
      root = datagate.get_item(request.getvalue('global_rootid', ''))
      comments = root.search1(name="comments")
      item = datagate.create_item(creatorid=creator.id, parentid=comments.id)
      item.text = text                # this is purely for the commenter view (so it knows what to show on the screen)
      item.versions = [ text ]        # a list to hold all versions of this comment
      item.authors = [ creator.id ]   # a list to hold all authors of the versions of this comment
      item.revisingnow = None         # who is revising the comment right now (if it's been assigned to someone)
      item.bestrevision = None        # the best revision (index in the versions list) once chosen
      item.bestrevisionauthor = None  # the best revision author (who selected the best one)
      item.save()
      return []  # comment doesn't show until it is revised and best one is picked
    finally:
      self.lock.release()
  
  
  def revise_comment_action(self, request):
    '''Revises a comment in the tree, then sends the edit event to update the screen'''
    self.lock.acquire()
    try:
      item = datagate.get_item(request.getvalue('itemid', ''))
      text = request.getvalue('text', '')
      author = request.session.user
      
      # update the tree
      item.versions.append(text)
      item.authors.append(author.id)
      item.revisingnow = None  # so others can now revise this item
      item.text = text  # this allows the regular commenter to update the view
      item.save()
      
      return []
      
    finally:
      self.lock.release()
      
      
      
  ###################################################
  ###   Administrator methods
      
  def initialize_activity(self, request, new_activity):
    '''Called from the Administrator.  Sets up the activity'''
    Commenter.initialize_activity(self, request, new_activity)
    new_activity.num_comment_revisions = 3
    new_activity.min_unrevised = 2
    new_activity.save()
    

  def send_admin_page(self, request):
    '''Sends an administrator page for this view.'''
    Commenter.send_admin_page(self, request)
    activity = datagate.get_item(request.getvalue('itemid', ''))
    
    request.writeln(request.cgi_form(gm_action='CommenterReviser.reviseoptions', itemid=activity.id))
    request.writeln('''
      <p>&nbsp;</p>
      <p><b>Options for Commenter with Revisions:</b></p>
      <div>Number of revisions per comment (including original): <input type=text size=3 name=num_comment_revisions value="''' + str(activity.getvalue('num_comment_revisions', 3)) + '''"></div>
      <div>Allow new comments when the number of comments needing revisions drops below: <input type=text size=3 name=min_unrevised value="''' + str(activity.getvalue('min_unrevised', 2)) + '''"></div>
      <div><input type=submit value="Save"></div>
      </form>
    ''')

  def reviseoptions_action(self, request):
    activity = datagate.get_item(request.getvalue('itemid', ''))
    activity.num_comment_revisions = int(request.getvalue('num_comment_revisions', '3'))
    activity.min_unrevised = int(request.getvalue('min_unrevised', '2'))
    activity.save()
    
      