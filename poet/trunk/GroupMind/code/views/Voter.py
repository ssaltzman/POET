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
import math
import sys

result_cols = [
  'Item',
  'Your Vote',
  'Mean',
  'Sum',
  'N',
  'Min',
  'Max',
  'Variance',
  'Std Dev'
]


########################################################################
###   The base of the specific vote types (likert, top n, etc.)
    
class BaseVote:
  '''The base of all vote specific classes.  Here to define the method templates.'''
  
  def initialize_vote(self, vote):
    '''Allows a subvote to initialize a vote when the vote type is changed to it'''
    pass
    
  def process_admin_actions(self, request, vote):
    '''Allows processing of admin actions by the specific vote class'''
    pass
  
  def send_admin_page(self, request, vote):
    '''Sends the administrator options for the specific vote class'''
    pass
  
  def send_vote_screen(self, request, vote, voteitems):
    '''Sends the vote items.  The calling method starts and ends the form.'''
    pass
    
  def record_vote(self, request, vote, voteitems, uservotes):
    '''Records a vote.  Returns the new user vote item if the vote was recorded.  If the vote
       was incomplete and cannot be recorded, it throws an exception.'''
    # record the vote    
    uservote = datagate.create_item(parentid=uservotes.id, creatorid=request.session.user.id)
    uservote.userid = request.session.user.id
    votechildren = voteitems.get_child_items()
    for i in range(len(votechildren)):
      votechild = votechildren[i]
      setattr(uservote, votechild.id, request.getvalue('vote' + votechild.id, ''))
    uservote.save()
    return uservote
    
  def send_results(self, request, vote, voteitems, uservotes, myvote):
    '''Shows the results screen'''
    # short circuit if we have not results yet
    uservotes_children = uservotes.get_child_items()
    if len(uservotes_children) == 0:
      request.writeln('<p align="center">No votes have been cast</p>')
      return
      
    # sum up and sort the results
    results = []
    for votechild in voteitems.get_child_items():
      # calculate basic statistics
      n = 0
      sum = 0.0
      minimum = None
      maximum = None
      vals = []
      for uservote in uservotes_children:
        val = getattr(uservote, votechild.id)
        vals.append(float(val))
        n += 1
        sum += float(val)
        if minimum == None: minimum = val
        else: minimum = min(minimum, val)
        if maximum == None: maximum = val
        else: maximum = max(maximum, val)
      mean = sum / n
      result = [ votechild.text ]
      if myvote == None: result.append('-')
      else: result.append(getattr(myvote, votechild.id))
      result.append(sum)
      result.append(round(sum/n, 2))
      result.append(n)
      result.append(minimum)
      result.append(maximum)
      variance = 0
      if len(vals) > 1:
        varianceNumerator = 0.0
        for val in vals: # have to go through again now that we have the mean
          varianceNumerator += math.pow(val - mean, 2)
        variance = varianceNumerator / (len(vals) - 1)
        result.append(round(variance, 2))
        result.append(round(math.sqrt(variance), 2))
      else:
        result.append('-')
        result.append('-')
      results.append(result)
      
    # sort the results
    sortcol = int(request.getvalue('sortcol', '6'))
    sortdirection = int(request.getvalue('sortdirection', '1'))
    if sortdirection == 1: results.sort(lambda a, b: cmp(b[sortcol], a[sortcol]))
    else: results.sort(lambda a, b: cmp(a[sortcol], b[sortcol]))
        
    # show the results table
    request.writeln('<center>')
    request.writeln('<table border=1 cellpadding=5 cellspacing=0>')
    request.writeln('<tr>')
    for i in range(len(result_cols)):
      request.write('<th>')
      sortdir = None
      if i == sortcol: 
        request.write('<u>')
        sortdir = -1 * sortdirection
      request.write('<a href="' + request.cgi_href(voteraction='results', sortcol=i, sortdirection=sortdir) + '">' + result_cols[i] + '</a>')
      request.writeln('</th>')
    request.writeln('</tr>')
    for result in results:
      request.writeln('<tr>')
      for i in range(len(result)):
        if i == 0: align = 'left'
        else: align = 'right'
        val = str(result[i])
        request.writeln('<td valign="top" align="' + align + '">' + val + '</td>')
      request.writeln('</tr>')
    request.writeln('</table>')
    request.writeln('<center>')
    
    
    
    
#############################################################
###   Specific vote type classes (likert, top n, etc.)    
    
  
class LikertVote(BaseVote):
  def initialize_vote(self, vote):
    '''Allows a subvote to initialize a vote when the vote type is changed to it'''
    if not hasattr(vote, 'likertscaleitems'):
      vote.likertscaleitems = 'Strongly Agree\nSomewhat Agree\nAgree\nSomewhat Disagree\nStrongly Disagree'
    vote.save()
    
  def process_admin_actions(self, request, vote):
    '''Allows processing of admin actions by the specific vote class'''
    action = request.getvalue('voteraction', '')
    if action == 'likertscale':
      vote.likertscaleitems = request.getvalue('scaleitems', '')
      vote.save()
  
  def send_admin_page(self, request, vote):
    '''Sends the administrator options for the specific vote class'''
    request.writeln('Available Likert Scale Selections:')
    request.writeln(request.cgi_form(voteraction='likertscale', scaleitems=None, startlow=None))
    request.writeln('<br>&nbsp;&nbsp;&nbsp;')
    request.writeln('(First item has a value of 1)')
    request.writeln('<br>&nbsp;&nbsp;&nbsp;')
    request.writeln('Enter one line per item:')
    request.writeln('<br>&nbsp;&nbsp;&nbsp;')
    request.write('<textarea rows="15" cols="30" name="scaleitems">')
    request.write(vote.likertscaleitems)
    request.writeln('</textarea>')
    request.writeln('<br>&nbsp;&nbsp;&nbsp;')
    request.writeln('<input type=submit value=Save>')
    request.writeln('</form>')
  
  def send_vote_screen(self, request, vote, voteitems):
    '''Sends the vote items.  The calling method starts and ends the form.'''
    request.writeln('<center>')
    request.writeln('<table border=1 cellpadding=5 cellspacing=0>')
    votechildren = voteitems.get_child_items()
    likertscaleitems = vote.likertscaleitems.split('\n')
    for i in range(len(votechildren)):
      votechild = votechildren[i]
      request.writeln('<tr>')
      request.writeln('<td nowrap valign=top>' + str(i+1) + '.</td>')
      request.writeln('<td valign=top>' + votechild.text + '</td>')
      request.writeln('<td nowrap valign=top><select name="vote' + votechild.id + '">')
      for j in range(len(likertscaleitems)):
        request.writeln('<option value="' + str(j+1) + '">' + likertscaleitems[j] + '</option>')
      request.writeln('</select></td>')
      request.writeln('</tr>')
    request.writeln('</table>')
    request.writeln('<center>')

  def send_results(self, request, vote, voteitems, uservotes, myvote):
    '''Shows the results screen'''
    BaseVote.send_results(self, request, vote, voteitems, uservotes, myvote)
    request.writeln('''
      <center>&nbsp;<br>
      <table border=0><tr><td>
      Points Key:
    ''')
    likertscaleitems = vote.likertscaleitems.split('\n')
    for j in range(len(likertscaleitems)):
      request.writeln('<br>' + str(j+1) + ' = ' + likertscaleitems[j])
    request.writeln('''
      </table>
      </td></tr></table>
      </center>
    ''')



  
class TopNVote(BaseVote):
  def initialize_vote(self, vote):
    '''Allows a subvote to initialize a vote when the vote type is changed to it'''
    if not hasattr(vote, 'num_selections'):
      vote.num_selections = '3'
    vote.save()
    
  def process_admin_actions(self, request, vote):
    '''Allows processing of admin actions by the specific vote class'''
    action = request.getvalue('voteraction', '')
    if action == 'setnumselections':
      vote.num_selections = request.getvalue('numselections', '')
      vote.save()
  
  def send_admin_page(self, request, vote):
    '''Sends the administrator options for the specific vote class'''
    request.writeln(request.cgi_form(voteraction='setnumselections', numselections=None))
    request.writeln('Number of selections:')
    request.writeln('<br>&nbsp;&nbsp;&nbsp;')
    request.writeln('<input name="numselections" type="text" size="10" value="' + vote.num_selections + '">')
    request.writeln('<input type="submit" value="Save">')
    request.writeln('</form>')
  
  def send_vote_screen(self, request, vote, voteitems):
    '''Sends the vote items.  The calling method starts and ends the form.'''
    request.writeln('<p align="center">Check your top ' + vote.num_selections + ' choice(s)</p>')
    request.writeln('<center>')
    request.writeln('<table border=1 cellpadding=5 cellspacing=0>')
    votechildren = voteitems.get_child_items()
    for i in range(len(votechildren)):
      votechild = votechildren[i]
      request.writeln('<tr>')
      request.writeln('<td nowrap valign=top>' + str(i+1) + '.</td>')
      request.writeln('<td nowrap valign=top><input type="checkbox" name="vote' + votechild.id + '" value="1"')
      if request.getvalue('vote' + votechild.id, '') == '1':
        request.writeln(' checked')
      request.writeln('>' + votechild.text + '</td>')
      request.writeln('</tr>')
    request.writeln('</table>')
    request.writeln('<center>')

  def record_vote(self, request, vote, voteitems, uservotes):
    '''Records a vote.  Returns the new user vote item if the vote was recorded.  If the vote
       was incomplete and cannot be recorded, it throws an exception.'''
    # ensure we have exactly the right number of items selected
    num_selections = 0
    for votechild in voteitems.get_child_items():
      if request.getvalue('vote' + votechild.id, '') == '1':
        num_selections += 1
    if num_selections != int(vote.num_selections):
      raise 'Please select exactly ' + vote.num_selections + ' items.'
    
    # record the vote    
    uservote = datagate.create_item(parentid=uservotes.id, creatorid=request.session.user.id)
    uservote.userid = request.session.user.id
    votechildren = voteitems.get_child_items()
    for i in range(len(votechildren)):
      votechild = votechildren[i]
      if request.getvalue('vote' + votechild.id, '') == '1': 
        setattr(uservote, votechild.id, '1') # set it manually because who knows what different browsers will send on an unchecked item
      else:
        setattr(uservote, votechild.id, '0')
    uservote.save()
    return uservote


  
class YesNoVote(BaseVote):
  '''A vote that allows a yes/no (1/0) for each item'''
  def send_vote_screen(self, request, vote, voteitems):
    '''Sends the vote items.  The calling method starts and ends the form.'''
    request.writeln('<center>')
    request.writeln('<table border=1 cellpadding=5 cellspacing=0>')
    votechildren = voteitems.get_child_items()
    for i in range(len(votechildren)):
      votechild = votechildren[i]
      request.writeln('<tr>')
      request.writeln('<td nowrap valign=top>' + str(i+1) + '.</td>')
      request.writeln('<td valign=top>' + votechild.text + '</td>')
      request.writeln('<td nowrap valign=top>')
      request.writeln('<input type="radio" name="vote' + votechild.id + '" value="1"')
      if request.getvalue('vote' + votechild.id, '') == '1':
        request.writeln(' checked')
      request.writeln('>Yes')
      request.writeln('<input type="radio" name="vote' + votechild.id + '" value="0"')
      if request.getvalue('vote' + votechild.id, '') == '0':
        request.writeln(' checked')
      request.writeln('>No')
      request.writeln('</td>')
      request.writeln('</tr>')
    request.writeln('</table>')
    request.writeln('<center>')

  def record_vote(self, request, vote, voteitems, uservotes):
    '''Records a vote.  Returns the new user vote item if the vote was recorded.  If the vote
       was incomplete and cannot be recorded, it throws an exception.'''
    # ensure we have an answer for all the items
    for votechild in voteitems.get_child_items():
      if request.getvalue('vote' + votechild.id, '') == '':
        raise 'Please answer all the vote items before submitting.'
    
    # send to the superclass to record it
    BaseVote.record_vote(self, request, vote, voteitems, uservotes)

  def send_results(self, request, vote, voteitems, uservotes, myvote):
    '''Shows the results screen'''
    BaseVote.send_results(self, request, vote, voteitems, uservotes, myvote)
    request.writeln('''
      <center>&nbsp;<br>
      Yes votes have a point value of 1
      <br>
      No votes have a point value of 0
    ''')

  


##################################################
###   Lookup structures for available vote types

vote_types = [
  ( 'Likert',  LikertVote ),
  ( 'Top N',   TopNVote ),
  ( 'Yes/No',  YesNoVote )
]
vote_classes = {}
for vote_type in vote_types:
  vote_classes[vote_type[0]] = vote_type[1]()



###############################################
###   The main vote class (the real view)

class Voter(BaseView):
  NAME = 'Voter'
  
  def __init__(self):
      BaseView.__init__(self)
     

  ############################################################
  ###   Initialization methods (for the view and for items)

  def initialize_activity(self, request, vote):
    '''Allows a view to customize a newly-created Activity.  Called from the Administrator when the 
       view is added to a meeting as an activity.'''
    # set the initial type of this view
    vote.type = vote_types[0][0]  
    vote_classes[vote_types[0][0]].initialize_vote(vote)
    vote.save()
       
    # create the items (holds the voting item text)
    vote_items = datagate.create_item(parentid=vote.id, creatorid=request.session.user.id)
    vote_items.node = 'VoteItems'
    vote_items.save()
    
    # create the user votes items (holds one child for each user's vote)
    user_votes = datagate.create_item(parentid=vote.id, creatorid=request.session.user.id)
    user_votes.node = 'UserVotes'
    user_votes.save()
    
    
  def initialize_item(self, request, item):
    '''Called when a new item is created by the event system and the event has an item_initializer parameter.
       This is called when the event parameters send an 'item_initializer' item.'''
    pass
    
    

  ############################################################
  ###   Administrator methods
    
  def send_admin_page(self, request):
    '''Sends an administrator page for this view.'''
    vote = datagate.get_item(request.getvalue('itemid', ''))
    
    # process actions
    self.process_admin_actions(request, vote)
    vote_classes[vote.type].process_admin_actions(request, vote)
    
    # header
    request.writeln(HTML_HEAD + HTML_BODY)
    request.writeln('<p align="center">Edit Voting Activity: ' + vote.name + '</p>')
    request.writeln('<table border=1 cellspacing=0 cellpadding=5 width=100%><tr><td valign="top">')
    request.writeln('<p align=center>Vote Options:</p>')
    
    # the voting type
    request.writeln(request.cgi_form(voteraction='changetype', type=None))
    request.writeln('Type of Vote:')
    request.writeln('<br>&nbsp;&nbsp;&nbsp;')
    request.writeln('<select name="type">')
    for vote_type in vote_types:
      request.write('<option value="' + vote_type[0] + '"')
      if vote_type[0] == vote.type: request.write(' selected')
      request.writeln('>' + vote_type[0] + '</option>')
    request.writeln('</select>')
    request.writeln('<input type=submit value=Change>')
    request.writeln('</form>')
    request.writeln('<p>&nbsp;</p>')
    
    # the options for each voting type
    vote_classes[vote.type].send_admin_page(request, vote)
    request.writeln('<p>&nbsp;</p>')

    # the items in the vote
    voteitems = vote.search1(node='VoteItems')
    request.writeln('</td><td valign="top">')
    request.writeln('<p align="center">Items To Vote On:</p>')
    if request.session.user.superuser == '1':
      request.writeln('<div align="right" style="padding: 3px">')
      request.writeln('<a href="' + request.cgi_href(voteraction='pasteclipboard') + '">Paste From Clipboard</a>')
      request.writeln('</div>')
    request.writeln('<p>&nbsp;</p>')
    request.writeln(request.cgi_form(voteraction='newvoteitem', text=None))
    request.writeln('<table border=0 width=100% cellpadding=5 cellspacing=0>')
    votechildren = voteitems.get_child_items()
    for i in range(len(votechildren)):
      votechild = votechildren[i]
      request.writeln('<tr>')
      request.writeln('<td nowrap valign=top align=center>' + str(i+1) + '.</td>')
      request.writeln('<td width=100% valign=top>' + votechild.text + '</td>')
      request.writeln('<td nowrap valign=top align=center>[ ')
      request.writeln('<a href="javascript:confirm_url(\'Delete this item?\', \'' + request.cgi_href(voteraction='deletevoteitem', votechildid=votechild.id) + '\');">Delete</a>')
      request.writeln(' ]</td>')
      request.writeln('</tr>')
    request.writeln('<tr>')
    request.writeln('<td nowrap valign=top align=center>&nbsp;</td>')
    request.writeln('<td width=100% valign=top>New Item: <input type=text size=50 name=text></td>')
    request.writeln('<td nowrap valign=top align=center><input type=submit value="Add"></td>')
    request.writeln('</tr>')
    request.writeln('</table>')
    request.writeln('</form>')
    request.writeln('<p>&nbsp;</p>')

    # footer
    request.writeln('</td></tr></table>')
    request.writeln('</body></html>')    
    
    
  def process_admin_actions(self, request, vote):
    action = request.getvalue('voteraction', '')
    if action == 'changetype':
      vote.type = request.getvalue('type', '')
      vote_classes[vote.type].initialize_vote(vote)
      vote.save()
      
    elif action == 'newvoteitem':
      voteitems = vote.search1(node='VoteItems')
      newitem = datagate.create_item(parentid=voteitems.id, creatorid=request.session.user.id)
      newitem.text = request.getvalue('text', '')
      newitem.save()
      
    elif action == 'deletevoteitem':
      datagate.del_item(request.getvalue('votechildid', ''))

    elif action == 'pasteclipboard':
      # get the data from the session object
      try:
        itemids = request.session.clipboarddata
      except AttributeError: # no clipboard data available
        return 
        
      # paste to the current root id
      events = []
      vote = datagate.get_item(request.getvalue('itemid', ''))
      parent = vote.search1(node='VoteItems')
      for itemid in itemids:
        if datagate.get_item(itemid):
          newitem = datagate.copy_deep(itemid, parent.id)
      
      



  ############################################################
  ###   Client view methods

  def send_content(self, request):
    # see if this user has already voted
    vote = datagate.get_item(request.getvalue('global_rootid', ''))
    voteitems = vote.search1(node='VoteItems')
    uservotes = vote.search1(node='UserVotes')
    myvote = uservotes.search1(userid=request.session.user.id)
    action = request.getvalue('voteraction', '')
    
    if myvote != None or action == 'results': # can't vote twice because we send them to the results page if they have a uservote
      self.send_results(request, vote, voteitems, uservotes, myvote)
      
    elif action == 'castvote':
      try:
        myvote = vote_classes[vote.type].record_vote(request, vote, voteitems, uservotes)
        self.send_results(request, vote, voteitems, uservotes, myvote)
      except:
        self.send_vote_screen(request, vote, voteitems, uservotes, myvote, sys.exc_info()[0])
      
    else:
      self.send_vote_screen(request, vote, voteitems, uservotes, myvote)
  

  
  def send_vote_screen(self, request, vote, voteitems, uservotes, myvote, error_message=None):
    # header
    request.writeln(HTML_HEAD + HTML_BODY)
    request.writeln('<div align="right" style="padding:3px"><a href="' + request.cgi_href(voteraction='results') + '">Skip Voting and View Results</a></div>')
    if error_message:
      request.writeln('<p align="center"><font color="#FF0000">' + str(error_message) + '</font></p>')
    request.writeln('&nbsp;&nbsp;&nbsp;&nbsp;Please vote on the following items:')
    params = {'voteraction':'castvote'}
    for voteitem in voteitems.get_child_items():
      params['vote' + voteitem.id] = None
    request.writeln(request.cgi_form(**params))
 
    # allow the subclass to write the specific vote screen
    vote_classes[vote.type].send_vote_screen(request, vote, voteitems)

    # footer
    request.writeln('<p align="center"><input type=submit value="Cast Vote"></p>')
    request.writeln('</form>')
    request.writeln("</body></html>")


  
  def send_results(self, request, vote, voteitems, uservotes, myvote):
    # header
    request.writeln(HTML_HEAD + HTML_BODY)
    request.writeln('<div align="right" style="padding:3px">')
    if myvote != None:
      request.writeln('You have voted on this poll')
    else:
      request.writeln('<a href="' + request.cgi_href(voteraction=None) + '">Cast Vote</a>')
    request.writeln('|')
    request.writeln('<a href="' + request.cgi_href(voteraction='results') + '">Refresh Results</a>')
    request.writeln('</div>')
    request.writeln('<p align="center">' + vote.type + ' Vote: ' + vote.name + '</p>')
    
    # allow the subclass to write the specific vote results
    vote_classes[vote.type].send_results(request, vote, voteitems, uservotes, myvote)
    
    # footer
    request.writeln("</body></html>")
    
    
