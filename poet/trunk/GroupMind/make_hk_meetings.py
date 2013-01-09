#!/usr/bin/python

import datagate
import Directory
import sys, random

TEMPLATE_MEETINGS =  [
 [ 'HK.DB.10.10.5.5.Template', 1, ],
 [ 'HK.DB.10.5.5.10.Template', 201, ],
 [ 'HK.DB.5.10.10.5.Template', 401, ],
 [ 'HK.DB.5.5.10.10.Template', 601, ],
 [ 'HK.ND.10.10.5.5.Template', 801, ],
 [ 'HK.ND.10.5.5.10.Template', 1001, ],
 [ 'HK.ND.5.10.10.5.Template', 1201, ],
 [ 'HK.ND.5.5.10.10.Template', 1401, ],
]

administrator = Directory.get_user_by_data('root', 'pass')
rand = random.Random()
ASCII_CHARS = 'abcdefghkmnopqrstuwxyz'
DIGIT_CHARS = '2345689'

for meetingname, start in TEMPLATE_MEETINGS:

  # get the template meeting
  for meeting in Directory.meetings_item.get_child_items():
    if meeting.name == meetingname:
      template_meeting = meeting
      break
  else:
    print 'Could not find meeting: ' + meetingname
    sys.exit(0)
    
  for i in range(start, start+120, 6):
    newmeetingname = meetingname[0:16] + str(i)
    print 'Creating meeting', newmeetingname
  
    # create the new meeting
#     meeting = datagate.copy_deep(template_meeting.id, Directory.meetings_item.id)
#     meeting.name = newmeetingname
#     meeting.save()
    
    # create and add the users
    for j in range(i, i+6):
      username = 'hk%4i' % j
      print '  Adding user', username
#       user = Directory.create_user(adminstrator.id)
#       user.name = username
#       user.password = ''
#       user.password += rand.choice(ASCII_CHARS)
#       user.password += rand.choice(ASCII_CHARS)
#       user.password += rand.choice(DIGIT_CHARS)
#       user.username = username
#       user.email = username
#       user.save()
#       groups_item = meeting.search1(name='groups')
#       group = groups_item.get_child_items()[0]
#       child = datagate.create_item(creatorid=template_meeting.creatorid, parentid=group.id)
#       child.user_id = user.id
#       child.save()
      
