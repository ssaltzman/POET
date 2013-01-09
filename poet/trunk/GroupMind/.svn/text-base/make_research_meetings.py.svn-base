#!/usr/bin/python

import datagate
import Directory
import sys

TEMPLATE_MEETING_NAME = '1NR-Template'
PREFIX = '1NR'
START = 1
END = 50

# get the template meeting
for meeting in Directory.meetings_item.get_child_items():
  if meeting.name == TEMPLATE_MEETING_NAME:
    template_meeting = meeting
    break
else:
  print 'Could not find meeting'
  sys.exit(0)
  
# create the meetings
for i in range(START, END+1):
  meeting_name = PREFIX + '%02i' % i
  print 'Creating meeting', meeting_name

  # find the user to add to this meeting
  user = Directory.users_item.search1(username=meeting_name)
  if not user:
    print 'Could not find user:', meeting_name
    sys.exit(0)
  
  # create the new meeting
  meeting = datagate.copy_deep(template_meeting.id, Directory.meetings_item.id)
  meeting.name = meeting_name
  meeting.save()
  
  # add the user
  groups_item = meeting.search1(name='groups')
  group = groups_item.get_child_items()[0]
  child = datagate.create_item(creatorid=template_meeting.creatorid, parentid=group.id)
  child.user_id = user.id
  child.save()
  
