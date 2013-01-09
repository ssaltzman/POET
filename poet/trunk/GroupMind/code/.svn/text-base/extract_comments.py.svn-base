#!/usr/bin/python

from picalo import *
from picalo.lib import GUID
from picalo.lib import stats
import re, sys
import Directory, datagate

###########################
###   Getting the data out
# get the meetings to go through
print 'Getting meetings'
meetings = Directory.meetings_item.get_child_items()

# open up the export files
meetings_table = Dataset.Table(['global_meetingid', 'meetingname', 'meetingtype'])
users_table = Dataset.Table(['global_meetingid', 'username', 'userid', 'numcomments', 'averagecommentlength', 'numratings', 'averagerating', 'stdevrating'])
comments_table = Dataset.Table(['commentid', 'userid', 'parentid', 'activity', 'comment', 'commentchars', 'commentwords', 'numratings', 'averagerating', 'stdevrating', 'sumrating'])
ratings_table = Dataset.Table(['ratingid', 'commentid', 'userid', 'rating'])

# go through the meetings
for meeting in meetings:
  print 'Working on', meeting.name
  
  groups = meeting.search1(name='groups').get_child_items()
  if len(groups) > 0:
    # meeting table
    rec = meetings_table.append()
    rec['global_meetingid'] = meeting.id
    rec['meetingname'] = meeting.name
    rec['meetingtype'] = meeting.name[meeting.name.find('.')+1: meeting.name.rfind('.')]
    
    # users table
    for user_item in groups[0]:
      user = Directory.get_user(user_item.user_id)
      rec = users_table.append()
      rec['global_meetingid'] = meeting.id
      rec['username'] = user.username
      rec['userid'] = user.id
    
    # comments and ratings
    for activity in meeting.search1(name='activities'):
      def recurse(item, activityname):
        for child in item:
          if child.getvalue('text', ''):
            rec = comments_table.append()
            rec['commentid'] = child.id
            rec['userid'] = child.creatorid
            rec['parentid'] = item.id
            rec['activity'] = activityname
            rec['comment'] = child.text
            rec['commentchars'] = len(child.text)
            rec['commentwords'] = len(child.text.split(' '))
            for key in child.get_data_keys('rating_.*'):
              rec = ratings_table.append()
              rec['ratingid'] = GUID.generate()
              rec['commentid'] = child.id
              rec['userid'] = key[key.rfind('_')+1:]
              rec['rating'] = int(child.getvalue(key))
          recurse(child, activityname)
      recurse(activity, activity.name.split(' ')[0])
      


print 'Saving'    
meetings_table.save_tsv(open('/tmp/meetings_table.tsv', 'w'))
users_table.save_tsv(open('/tmp/users_table.tsv', 'w'))
comments_table.save_tsv(open('/tmp/comments_table.tsv', 'w'))
ratings_table.save_tsv(open('/tmp/ratings_table.tsv', 'w'))