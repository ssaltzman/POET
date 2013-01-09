'''
Approved for Public Release: 12-3351. Distribution Unlimited
			(c)2012-The MITRE Corporation. 
Licensed under the Apache License, Version 2.0 (the "License");
			you may not use this file except in compliance with the License.
			You may obtain a copy of the License at
			http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
'''

from django.db import models
from django.db.models import get_model
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime

#we use Django's built-in User class to take advantage of their
#authentication tools. 
# if not u.get_profile().created_own_password:
class UserProfile(models.Model):
	user = models.ForeignKey(User, unique=True)
	created_own_password = models.BooleanField(default=False)
	password_last_updated = models.DateTimeField('time of last password update', default=datetime.datetime.now())
	bad_password_count = models.IntegerField(default=0)
	lockout_timer = models.DateTimeField(default=datetime.datetime.now())
	def lockout(self): #called when a password is given
		if (datetime.datetime.now() - self.lockout_timer).seconds > (15 * 60): #If it's been more than 15 minutes since the last bad password attempt...
			self.user.is_active = True
			self.user.save()
			self.bad_password_count = 0
			self.save()
			return #False
		elif self.bad_password_count < 5:
			return #False
		else:
			if self.user.is_active:
				self.user.is_active = False
				self.user.save()
			return #True
	def __unicode__(self):
		if self.user.get_full_name():
			return self.user.get_full_name()
		else:
			user_name = self.user.username

#a program, before adding data, is just a name and a list of its participants.
#data will ending up belonging to a particular program through a foreign key field

class Program(models.Model):
	name = models.CharField(max_length=200, primary_key=True)
	participants = models.ManyToManyField(User, through='Participant')
	'''a "top-locked" program should:
		a) Not allow non-admins to add top-level nodes
		b) Not include top-level nodes as voting possibilities
		c) Automatically include top-level nodes when importing to a new activity
	'''
	top_locked = models.BooleanField(default=False) 
	def activity_list(self):
		a_list = self.activity_set.all()
		return map(Activity.fetch_child, a_list)
	def __unicode__(self):
		return self.name

#Activity seems like an abstract model, since there's no such thing as "just an activity" without
#a type. However, "all of a program's activities" is a common query, and rather than have to remash
#together every non-abstract Activity database table every time that query is called, it's easier just
#to leave Activity as non-abstract. 
class Activity(models.Model):
	ACTIVITY_STATES = (
		('O', 'OPEN'),
		('P', 'PAUSED'),
		('C', 'CLOSED')
	)	
	program = models.ForeignKey(Program)
	name = models.CharField(max_length=200)
	nodes = models.ManyToManyField('Node', null=True, blank=True) 
	state = models.CharField(max_length=1, choices=ACTIVITY_STATES, default='O')
	#type removed
	#n removed
	def get_type(self):
		try: 
			self.brainstorming
		except Brainstorming.DoesNotExist: 
			pass
		else:
			return "Brainstorming"
		try: 
			self.pairwise
		except Pairwise.DoesNotExist: 
			pass
		else:
			return "Pairwise"
		try:
			self.topn
		except TopN.DoesNotExist:
			pass
		else:
			return "TopN"
		return "Unknown"
		
	def fetch_child(self):
		try: 
			return self.brainstorming
		except Brainstorming.DoesNotExist: 
			pass
		try: 
			return self.pairwise
		except Pairwise.DoesNotExist: 
			pass
		try:
			return self.topn
		except TopN.DoesNotExist:
			pass
		raise RuntimeError("Activity Type unknown")
		
	class Meta:
		verbose_name_plural = "Activities"
	def __unicode__(self):
		return "[%s] %s: %s" % (self.program.name, self.name, self.get_type())

class Brainstorming(Activity):
	#top_locked = models.BooleanField(default=False) 
	def activity_type(self):
		return get_model("brainstorming", "Brainstorming")
	#def activity_type2(self):
	#	return self.__class__
	class Meta:
		verbose_name_plural = "Brainstorming Activities"
	def __unicode__(self):
		return "[%s] %s: Brainstorming" % (self.program.name, self.name)

class Pairwise(Activity):
	def activity_type(self):
		return get_model("brainstorming", "Pairwise")
	class Meta:
		verbose_name_plural = "Pairwise Comparison Activities"
	def __unicode__(self):
		return "[%s] %s: Pairwise Comparison" % (self.program.name, self.name)

class TopN(Activity):
	n = models.PositiveIntegerField()
	def activity_type(self):
		return get_model("brainstorming", "TopN")
	class Meta:
		verbose_name_plural = "Top N Vote Activities"
	def __unicode__(self):
		#print "type: ", type(self.n)
		return "[%s] %s: Top %s Vote" % (self.program.name, self.name, self.n)

ACTIVITY_TYPES = (
	('Brainstorming',  'Brainstorming'),
	('TopN',  'Top N Voting'),
	('Pairwise',  'Pair-Wise Comparison'),
)

class Group(models.Model):
	name = models.CharField(max_length=200)
	program = models.ForeignKey(Program)
	def __unicode__(self):
		return "[%s] %s" % (self.program, self.name)
		
#a participant is a unique combination of a program and a user. It's responsible
#for tracking each user's program membership and role
class Participant(models.Model):
	program = models.ForeignKey(Program)
	user = models.ForeignKey(User)
	admin = models.BooleanField(default=False)
	group = models.ForeignKey(Group)
	#limit_choices_to = {'program': self.program},
	activity = models.ForeignKey(Activity, null=True, blank=True)
	
	class Meta:
		unique_together = (("program", "user"),) #Django has no multi-field primary keys. Unique_together is the suggested solution
		ordering = ['program']
	def __unicode__(self):
		if self.admin:
			admin_state = "[ADMIN] "
		else:
			admin_state = ""
		if self.user.get_full_name():
			user_name = self.user.get_full_name()
		else:
			user_name = self.user.username
		return "%s %s in %s" % (admin_state, user_name, self.program.name)
						
#given a node, n:
#retrieving n's parent: n.parent_node
#retrieving n's children: n.children.all()  
class Node(models.Model):
	parent_node = models.ForeignKey('self', related_name='children', null=True, blank=True)
	author = models.ForeignKey(Participant, related_name='author')
	last_edit_by = models.ForeignKey(Participant, related_name='last_edit_by', null=True, blank=True)
	editable = models.BooleanField(default=True)
	
	text = models.TextField()
	image = models.ImageField(upload_to="node_images/", null=True, blank=True)
	video = models.FileField(upload_to="node_videos/", null=True, blank=True)
	sub_time = models.DateTimeField('time submitted', default=datetime.datetime.now())
	updated_time = models.DateTimeField('last updated', default=datetime.datetime.now())
	def __unicode__(self):
		if len(self.text) < 20:
			return "%s: %s" % (self.author.user.first_name, self.text)
		else:
			return "%s: %s..." % (self.author.user.first_name, self.text[0:20])
		
class TopNVote(models.Model):
	activity = models.ForeignKey(Activity) #, related_name='activity')
	participant = models.ForeignKey(Participant) #, related_name='participant')
	vote = models.CommaSeparatedIntegerField(max_length=200, null=True, blank=True)
	def getVote(self):
		return self.vote.split(',')
	def __unicode__(self):
		return "%s: %s" % (self.participant.user.first_name, self.vote)
	#I should add a function to get vote as a proper list, instead of doing it in views

class PairwiseVote(models.Model):
	VOTE_TYPES = (
		('A', 'Item A'),
		('B', 'Item B'),
		('E', 'Equal / No Preference'),
		('N', 'Not enough information'),
		('S', 'Skip'),
	)
	activity = models.ForeignKey(Activity)
	participant = models.ForeignKey(Participant)
	node1 = models.ForeignKey(Node, related_name='node1')
	node2 = models.ForeignKey(Node, related_name='node2')
	vote = 	models.CharField(max_length=3, choices=VOTE_TYPES, null=True, blank=True)
	def __unicode__(self):
		if self.vote == 'A':
			return self.participant.user.first_name+": "+self.node1.text+" > "+self.node2.text
		elif self.vote == 'B':
			return self.participant.user.first_name+": "+self.node2.text+" > "+self.node1.text
		elif self.vote == 'E':
			return self.participant.user.first_name+": "+self.node1.text+" = "+self.node2.text
		return self.participant.user.first_name+": "+self.node1.text+" ? "+self.node2.text
		
	'''Survey Models'''
class Survey(models.Model):
	program = models.ForeignKey(Program)
	name = models.CharField(max_length=200)
	visible = models.BooleanField(default=False)
	def __unicode__(self):
		return "[%s] %s" % (self.program, self.name)

class SurveyGroup(models.Model):
	survey = models.ForeignKey(Survey)
	name = models.CharField(max_length=200)
	def __unicode__(self):
		return "[%s] %s" % (self.survey, self.name)

class SurveyRespondent(models.Model):
	group = models.ForeignKey(SurveyGroup)
	name = models.CharField(max_length=200)
	def __unicode__(self):
		return "[%s] %s" % (self.group, self.name)

class SurveyQuestion(models.Model):
	survey = models.ForeignKey(Survey)
	question = models.CharField(max_length=300)
	Pvalue = models.FloatField()
	def __unicode__(self):
		return "[%s] (%s) %s..." % (self.survey, self.Pvalue, self.question[0:80])

class SurveyDataPoint(models.Model):
	respondent = models.ForeignKey(SurveyRespondent)
	question = models.ForeignKey(SurveyQuestion)
	value = models.IntegerField()
	#comment = models.CharField(max_length=300)
	def __unicode__(self):
		return "%s voted %i on %s..." % (self.respondent.name, self.value, self.question.question[0:80])