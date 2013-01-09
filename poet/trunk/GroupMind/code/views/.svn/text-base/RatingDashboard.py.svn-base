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


from Constants import *
import Directory
import datagate
import BaseView
import TimedDict
import math
import time
import threading



def _format_csv(field):
  '''Formats a value for CSV export'''
  qualifier = '"'
  double_qualifier = '""'
  delimiter = ','
  field = str(field)
  field = field.replace(qualifier, double_qualifier)
  if field.find(delimiter) >= 0:
    field = qualifier + field + qualifier
  return field





class ScoreHistory:
  '''Simple data class used to keep score histories for each user in a meeting.  It's sort
     of like a queue, but with special behavior.'''
  def __init__(self):
    self.lock = threading.RLock()
    self.history = []
    
  def push(self, score):
    '''Pushes a new score onto the stack'''
    self.lock.acquire()
    try:
      self.history.append( (time.time(), score) )
    finally:
      self.lock.release()
    
  def pop(self, time):
    '''Retrieves the score closest to (but not surpassing) the given time, and 
       clears the returned score as well as all previous items on the queue'''
    self.lock.acquire()
    try:
      # find the first item that has a time greater than the given time
      i = 0
      while i < len(self.history) and self.history[i][0] < time:
        i += 1
      if i > 0 and i <= len(self.history):
        score = self.history[i - 1][1]
        self.history = self.history[i:]
        return score
      return None
    finally:
      self.lock.release()



class RatingDashboard(BaseView.BaseView):
  NAME = 'Rating'
  rights_list = [ 'View Tree', 'View Author', 'Add Sibling', 'Add Child', 'Edit', 'Delete', 'Comment Visibility', 'Rate Comments', 'Comment Rating Feedback', 'Number of Ratings', 'Overall Group Feedback', 'Overall User Feedback', 'Individual Pacing' ]
  
  def __init__(self):
    BaseView.BaseView.__init__(self)
    self.interactive = 0
    self.score_history = TimedDict.TimedDict()
    self.meeting_timer = TimedDict.TimedDict()
    self.meeting_goals = TimedDict.TimedDict()

    
  def _get_individual_scores(self, indivs, id):
    '''Returns the scores dict for the given individual id, creating it if necessary'''
    # get the right individual
    if not indivs.has_key(id):
      indivs[id] = { 'numRatings': 0, 'numComments': 0, 'ratingsScore': 0.0 }
    return indivs[id]
    
    
  def send_content(self, request):
    '''The top feedback frame'''
    # this is quite a process, but I've timed it on my Mac G4 and it only takes 0.01 seconds
    # on faster server, it would go even faster (the G4's not that fast compared to a dedicated server)
    rights = self.get_user_rights(request)
    
    # get the activity and treeroot
    activity = datagate.get_item(request.getvalue('global_rootid', ''))
    ratingRefreshRate = 20000
    if hasattr(activity, 'ratingRefreshRate'):
      try: ratingRefreshRate = int(activity.ratingRefreshRate) * 1000
      except TypeError: pass
    
    # calculate the individual scores (we calculate for all individuals)
    indivs = {}
    ratingnames = self.get_rating_names(activity)
    ratinginfo = dict( [ (ratingname, self.get_rating_adjustment(activity, ratingname)) for ratingname in ratingnames ] )
    for item in activity.get_parent().get_child_items(deep=1):

      # combine the ratings for this item into a data structure that we can access easily
      raters = {}
      for key in item.__dict__.keys():
        if key.find('rating_') == 0:
          parts = key.split('_')
          if len(parts) == 3: 
            dummy, rating, raterid = parts
            if not raters.has_key(raterid):
              raters[raterid] = {}
            raters[raterid][rating] = int(getattr(item, key)) * ratinginfo[rating] # rating * adjustment
    
      # add a comment point for the author of this item
      self._get_individual_scores(indivs, item.creatorid)['numComments'] += 1
      
      # add points for the ratings score
      if len(raters) > 0:
        total = 0.0
        for user_ratings in raters.values():
          user_product = 1
          for rating in user_ratings.values():
            user_product *= rating
          total += user_product
        average = total / len(raters)
      else:
        average = 0.0
      self._get_individual_scores(indivs, item.creatorid)['ratingsScore'] += average

      # add a rating point to everyone who rated this comment
      for raterid in raters.keys():
        self._get_individual_scores(indivs, raterid)['numRatings'] += 1
          
    # drop off the administrator
    for user in Directory.get_users():
      if user.superuser == '1' and indivs.has_key(user.id):
        del indivs[user.id]
        
    # calculate the group averages
    group = { 'numCommentsTotal': 0.0, 'ratingsScoreTotal': 0.0, 'numRatingsTotal': 0.0, 'numComments': 0.0, 'ratingsScore' : 0.0, 'numRatings': 0.0 }
    if len(indivs) > 0:
      for indiv in indivs.values():
        group['numCommentsTotal'] += indiv['numComments']
        group['ratingsScoreTotal'] += indiv['ratingsScore']
        group['numRatingsTotal'] += indiv['numRatings']
      group['numComments'] = group['numCommentsTotal'] / len(indivs)
      group['ratingsScore'] = group['ratingsScoreTotal'] / len(indivs)
      group['numRatings'] = group['numRatingsTotal'] / len(indivs)

    # save any goal/timer changes from the administrator      
    bars = 30
    elapsed_time = 0
    timer_duration = 0
    goal = 100

    # get the meeting timer/goal info from the admin if he's saved something
    if self.meeting_timer.has_key('z'): # do we have a timer for this meeting?
      timer_start, timer_duration, goal = self.meeting_timer['z']
      elapsed_time = time.time() - timer_start
      
    # calculate the scale and number of goal bars
    scale = float(bars) / float(goal)
    num_goal_bars = goal * scale
    if timer_duration <= 0 or elapsed_time >= timer_duration:
      num_elapsed_goal_bars = num_goal_bars
    else:
      num_elapsed_goal_bars = num_goal_bars * (elapsed_time / float(timer_duration))
              
    # adjust for the multiplier
    myratings = self._get_individual_scores(indivs, request.session.user.id)
    myratings['numRatingsN'] = myratings['numRatings']
    myratings['numRatings'] *= float(activity.ratingMultiplier)
    myratings['numCommentsN'] = myratings['numComments']
    myratings['numComments'] *= float(activity.commentMultiplier) 
    myratings['ratingsScoreN'] = ''
    myratings['ratingsScore'] *= float(activity.ratingsScoreMultiplier)
    myscore = myratings['numRatings'] + myratings['numComments'] + myratings['ratingsScore']
    group['numRatings'] *= float(activity.ratingMultiplier) 
    group['numComments'] *= float(activity.commentMultiplier) 
    group['ratingsScore'] *= float(activity.ratingsScoreMultiplier) 
    groupscore = group['numRatings'] + group['numComments'] + group['ratingsScore']
    
    # history for individual pacing
    pacing_message = ''
    if rights['Individual Pacing']:
      myspeedscore = myratings['numRatings'] + myratings['numComments']
      # ensure I have a history object
      history_key = request.getvalue('z', request.session.user.id) + activity.id
      if not self.score_history.has_key(history_key):
        self.score_history[history_key] = ScoreHistory()
      
      # push my current score
      self.score_history[history_key].push(myspeedscore)
      
      # pop my old score from duration seconds ago and set the message
      oldscore = self.score_history[history_key].pop(time.time() - int(activity.pacingDuration))
      if oldscore != None:
        score_diff = myspeedscore - oldscore
        levels = activity.pacingValues.strip().split('\n')
        for i in range(len(levels)):
          line = levels[i]
          line = line.strip()
          pos = line.find(' ')
          if pos > 0:
            if float(line[0:pos]) <= score_diff: 
              pacing_message = line[pos+1:]
              break
        if pacing_message == '':
          pacing_message = levels[-1]
              
        # log the new entry to the log file
        if activity.pacingLogFile != None and activity.pacingLogFile != '':
          self.log_file_lock.acquire()
          try:
            f = open(activity.pacingLogFile, 'a')
            log_vals = [ 
              str(time.time()), 
              request.getvalue('z', ''), 
              request.session.user.id, 
              _format_csv(request.session.user.username), 
              activity.id, 
              _format_csv(pacing_message),
              str(score_diff),
              str(myscore), 
              str(myspeedscore),
              str(myratings['numRatings']),
              str(myratings['numRatingsN']),
              str(myratings['numComments']),
              str(myratings['numCommentsN']),
              str(myratings['ratingsScore']),
              str(myratings['ratingsScoreN']),
              str(groupscore),
              str(group['numRatings']),
              str(group['numComments']),
              str(group['ratingsScore']),
            ]
            f.write(','.join(log_vals))
            f.write('\n')
            f.close()
          finally:
            self.log_file_lock.release()
              
    # send the HTML          
    images = [ 
      ("Ratings Submitted", 'numRatings', 'bar-blue.png'), 
      ("Comments Submitted", 'numComments', 'bar-blue.png'), 
      ("Comment Quality Score", 'ratingsScore', 'bar-blue.png') 
    ]
    request.writeln(HTML_HEAD_NO_CLOSE + '''
        <script language='JavaScript' type='text/javascript'>
          function refreshEvents() {
            window.location.replace("''' + request.cgi_href() + '''");
          }
          function enableRefresh() {
            window.setTimeout('refreshEvents()', ''' + str(ratingRefreshRate) + ''');        
          }
        </script>      
      </head>
    ''')
    request.writeln('<body bgcolor="#EEEEFF" onload="javascript:enableRefresh();">')
    request.writeln('<table border=0 cellspacing=0 cellpadding=0 width="100%"><tr><td valign="top">')
    request.writeln('<table border=0 cellspacing=0 cellpadding=0>')
    for title, key, image in images:
      request.writeln('<tr>')
      request.writeln('<td>&nbsp;&nbsp;' + str(myratings[key+'N']) + ' ' + title + '</td>')
      request.writeln('<td>&nbsp; = ' + str(int(round(myratings[key]))) + ' points</td>')
      request.writeln('</tr>')
    request.writeln('</table>')
    request.writeln('</td><td align="center" valign="center">')
    request.writeln(pacing_message)
    request.writeln('</td><td align="center" valign="top">')
    request.writeln('<table border=0 cellspacing=0 cellpadding=0>')
    for title, scores, overall in [ ("Goal", None, goal), ("Individual", myratings, myscore), ("Group Average", group, groupscore) ]:
      request.write('<tr>')
      request.write('<td noWrap align="right"><b>' + title + ':</b></td>')
      request.write('<td noWrap>&nbsp;&nbsp;</td>')
      request.write('<td noWrap>')
      if scores: # the individual and group
        for title, key, image in images:
          for i in range(0, int(scores[key] * scale)):
            request.write('<img alt="*" src="' + join(WEB_PROGRAM_URL, image) + '">')
        request.write(' [' + str(int(round(overall))) + ' points]')
      else: # the goal
        for i in range(0, int(num_goal_bars)):
          if i <= num_elapsed_goal_bars:
            request.write('<img alt="*" src="' + join(WEB_PROGRAM_URL, 'bar-black.png') + '">')
          else:
            request.write('<img alt="*" src="' + join(WEB_PROGRAM_URL, 'bar-white.png') + '">')
        if request.session.user.superuser == '1':
          request.write(request.cgi_form(gm_action='RatingDashboard.timer', timerstart=None, timerduration=None, goal=None))
          request.write(' [ <input type=text size=4 name="goal" value="' + str(overall) + '"> points]')
          request.write('<input type=submit value="Set"><br>')
          request.write(' (Timer: <input type=text size=4 name="timerstart" value="' + str(int(elapsed_time)) + '">/<input type=text size=4 name="timerduration" value="' + str(timer_duration) + '"> secs')
          request.write(')')
          request.write('</form>')
        else:
          request.write(' [' + str(overall) + ' points]')
      request.writeln('</td>')
      request.writeln('</tr>')
    request.writeln('</table>')
    request.writeln('</td></tr></table>')
    request.writeln('</body>')
    request.writeln('</html>')


  def timer_action(self, request):
    goal = 100
    activity = datagate.get_item(request.getvalue('global_rootid', ''))
    self.meeting_timer['z'] = (
      time.time() - int(request.getvalue('timerstart', '0')), 
      int(request.getvalue('timerduration', '0')),
      int(request.getvalue('goal', goal))
    )
  
   
  def get_rating_names(self, activity):
    '''Returns a list of rating names that exist for this view'''
    names = []
    for key in activity.__dict__.keys():
      if len(key) > 8 and key[0:7] == 'rating_':
        names.append(key[7:])
    return names
    
  def get_rating_options(self, activity, name):
    '''Returns the rating options for a given rating name as a list of tuples: (value, text)'''
    options = []
    for line in getattr(activity, 'ratinginfo_' + name + '_options').strip().split('\n'):
      line = line.strip()
      pos = line.find(' ')
      if pos > 0:
        options.append((int(line[0:pos]), line[pos+1:]))
    return options
    
    
  def get_rating_max_option_value(self, activity, name):
    '''Returns the maximum rating value for the given rating name in the given activity'''
    options = self.get_rating_options(activity, name)
    if len(options) == 0:
      return 0
    val = options[0][0]
    for option in options:
      val = max(val, option[0])
    return val
    
    
  def get_rating_adjustment(self, activity, name):
    '''Returns the adjustment value for the given rating name in the given activity as an int'''
    return int(getattr(activity, 'ratinginfo_' + name + '_adjustment'))
    
   