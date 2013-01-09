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

from brainstorming.models import UserProfile, Program, Group, Participant, Node, Activity, Brainstorming, TopN, Pairwise, TopNVote, PairwiseVote, ACTIVITY_TYPES
from brainstorming.models import Survey, SurveyQuestion, SurveyRespondent, SurveyGroup, SurveyDataPoint
from django.contrib.auth.models import User#, Permission
from django.db.models import get_model, F, Q #F Q too, Django
#from django.contrib.admin.models import LogEntry
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import simplejson #necessary?
from django.db import IntegrityError
from django.conf import settings
import datetime
import os, sys #for thumbnail creation
import random #for pairwise voting
from PIL import Image #for thumbnail creation
from django.utils.datastructures import MultiValueDictKeyError #for form validation
import logging		
import re
import csv #for survey data
import itertools		
from operator import attrgetter #a function factory for grabbing named attributes
from brainstorming.kw import *

logger = logging.getLogger('Access_Logger')
		
''' Authentication Functions '''
def login(request, next=''):
	if request.method == 'GET':
		if request.user.is_authenticated():
			return HttpResponseRedirect('/')
		next_url = request.GET.get('next')
		if not next_url:
			next_url = "/"
		return render_to_response('registration/login.html', {'next_url': next_url}, context_instance=RequestContext(request))
	else: 
		username = request.POST.get('username', 'didnotgetuser')
		password = request.POST.get('password', 'didnotgetpassword')
		next_url = request.POST.get('next_url', '')
		user = authenticate(username=username, password=password)
		if user is not None: 
			try: #this should only be necessary for the root user, the first time he logs in
                                user_profile = user.get_profile()
                        except UserProfile.DoesNotExist:
                                user_profile = UserProfile(user=user, created_own_password=False)
                                user_profile.save()
                        user_profile.lockout() #lock or unlock the account as needed

			if user.is_active:
				auth_login(request, user)
				request.session.set_expiry(60*60) #one hour before session expires
				logger.info("[AUTH]     %s (%s) logged in." % (request.user, request.META["REMOTE_ADDR"]))
				return HttpResponseRedirect(next_url)
			else:
				# this could be a "disabled account" error page
				auth_logout(request)
				logger.warning("[AUTH]     Login %s from %s failed: account locked out." % (username, request.META["REMOTE_ADDR"]))
				return render_to_response('registration/login.html', {'error_message': "Too many bad attempts. Your account is temporarily disabled."}, context_instance=RequestContext(request))
		else:
			try: 
				#print username
				user = User.objects.get(username=username)
			except User.DoesNotExist: #wrong username
				logger.warning("[AUTH]     Login %s from %s failed: invalid username." % (username, request.META["REMOTE_ADDR"]))
				return render_to_response('registration/login.html', {'error_message': "Invalid login.", 'next_url': next_url}, context_instance=RequestContext(request))
			else:
				try:
					user_profile = user.get_profile()
				except UserProfile.DoesNotExist: #real username, but no profile
					user_profile = UserProfile(user=request.user, created_own_password=False)
					user_profile.save()
				user_profile.lockout() #first, we wipe out their bad_password_count if it's been more than 15 minutes
				#user_profile.bad_password_count = F('bad_password_count') + 1 #prevents race condition
				user_profile.lockout_timer = datetime.datetime.now() #then we update their last bad password timer
				user_profile.bad_password_count = user_profile.bad_password_count + 1
				user_profile.save()
				#user_profile = user.get_profile() #with F objects, you have to reload the object after saving. 
				logger.warning("[AUTH]     Login %s from %s failed: invalid password (attempt %i)." % (username, request.META["REMOTE_ADDR"], user_profile.bad_password_count))
				#then we return to the login screen with a generic error message. 
				return render_to_response('registration/login.html', {'error_message': "Invalid login.", 'next_url': next_url}, context_instance=RequestContext(request))
				

def logout(request):
	logger.info("[AUTH]     %s (%s) logged out." % (request.user, request.META["REMOTE_ADDR"]))
	auth_logout(request)
	return HttpResponseRedirect('/login')

#input: a request and, optionally, a program, an activity, an "adminRequired" flag or a "user to be managed"
#output: False if the user has permission, a redirect otherwise
def authCheck(request, program=None, activity=None, adminRequired=False, user=None, survey_id=None):
	if not request.user.is_authenticated(): 
		#might be redundant with above, but better safe than sorry
		#No user is logged in. Redirect to login screen:
		logger.info("[ACCESS]   USER: <no user> REQUEST: %s RESULT: Redirecting to login. REASON: Not logged in." % (request.path))
		return HttpResponseRedirect('/login/?next=%s' % request.path)
	#this will be unnecessary, once all users are created through the proper interface
	'''
	try: 
		user_profile = request.user.get_profile()
	except UserProfile.DoesNotExist:
		user_profile = UserProfile(user=request.user, created_own_password=False)
		user_profile.save()
	except AttributeError: #anonymous users don't even have a get_profile() 
                #No user is logged in. Redirect to login screen:
                logger.info("[ACCESS]   USER: <no user> REQUEST: %s RESULT: Redirecting to login. REASON: Not logged in." % (request.path))
                return HttpResponseRedirect('/login/?next=%s' % request.path)
	'''
	#if user_profile.lockout():
	#	logger.info("[ACCESS]   USER: %s REQUEST: %s RESULT: Denied. REASON: Account locked out (SHOULD NOT HAVE BEEN LOGGED IN, WHAT HAPPENED?)." % (request.user, request.path))
	#	return HttpResponseRedirect('/login/?next=%s' % request.path)
	if request.user.is_superuser:
		#You're a superuser? Proceed. 
		logger.info("[ACCESS]   USER: %s REQUEST: %s RESULT: Granted. REASON: Superuser." % (request.user, request.path))
		return False
	if user == request.user:
		#if you're already on your way to managing yourself, go right ahead
		logger.info("[ACCESS]   USER: %s REQUEST: %s RESULT: Granted. REASON: Attempt to access own settings." % (request.user, request.path))
		return False
	if not request.user.get_profile().created_own_password:
		#if you're not on your way to managing yourself but you need to set your password, you're going there first
		logger.info("[ACCESS]   USER: %s REQUEST: %s RESULT: Redirecting to settings. REASON: User must set own password." % (request.user, request.path))
		messages.warning(request, "You must set your password before continuing.")
		return HttpResponseRedirect('/manageuser/%i'%request.user.id)
	if user:
		if not request.user.is_staff:
			logger.warning("[ACCESS]   USER: %s REQUEST: %s RESULT: Redirecting to /. REASON: Attempt to manage user but is not staff." % (request.user, request.path))
			messages.warning(request, "You must be a member of the staff to edit another user.")
			return HttpResponseRedirect('/')
		elif user.is_staff:
			logger.warning("[ACCESS]   USER: %s REQUEST: %s RESULT: Redirecting to /. REASON: Attempt to manage staff but is not superuser." % (request.user, request.path))
			messages.warning(request, "You cannot edit a fellow staff member.")
			return HttpResponseRedirect('/')
	if program:
		try:
			participant = Participant.objects.get(program=program, user=request.user)
		except Participant.DoesNotExist:
			#The user is attempting to access a program of which they are not a participant.
			logger.warning("[ACCESS]   USER: %s REQUEST: %s RESULT: Redirecting to /. REASON: Attempt to access program but is not participant." % (request.user, request.path))
			messages.warning(request, "Could not access Program.")
			return HttpResponseRedirect('/')
		if not participant.admin and adminRequired:
			logger.warning("[ACCESS]   USER: %s REQUEST: %s RESULT: Redirecting to /. REASON: Attempt to manage program but is not admin." % (request.user, request.path))
			messages.warning(request, "You are not an administrator of that program.")
			return HttpResponseRedirect('/')
		#this should only affect users who are trying to access an activity through the URL bar
		#users who are redirected to an activity will not be authChecked a second time		
		elif activity: 
			if not participant.admin and ((not participant.activity) or (participant.activity.id != activity.id)):
				#The user is not in an activity, or doesn't belong to any activity.
				logger.warning("[ACCESS]   USER: %s REQUEST: %s RESULT: Redirecting to program. REASON: Attempt to access activity but is not assigned." % (request.user, request.path))
				messages.warning(request, "You are not currently in that activity.")
				return HttpResponseRedirect("/%s/"%program.name)
		elif survey_id:
			survey = Survey.objects.get(id=survey_id)
			if not (participant.admin or survey.visible): #either being an admin or the survey being visible is sufficient
				logger.warning("[ACCESS]   USER: %s REQUEST: %s RESULT: Redirecting to program. REASON: Attempt to access not-visible survey data." % (request.user, request.path))
				messages.warning(request, "You are not permitted to view that survey.")
				return HttpResponseRedirect("/%s/"%program.name)		
	logger.info("[ACCESS]   USER: %s REQUEST: %s RESULT: Granted. REASON: Credentials satisfactory." % (request.user, request.path))
	return False

def manageuser(request, user_id=None):
	d = {}
	if request.method == 'GET':
		if user_id:
			edit_user = User.objects.get(pk=user_id)
			d["edit_user"] = edit_user
			redirect = authCheck(request, user=edit_user)
			if redirect:	
				return redirect
		elif not request.user.is_staff:
			return HttpResponseRedirect('/')
		else:
			redirect = authCheck(request)
			if redirect:	
				return redirect
		return render_to_response('management/manageuser.html', d, context_instance=RequestContext(request))
	else:
		try: 
			user = User.objects.get(pk=request.POST["edit_user_id"])
			logger.info("[EDITUSER] %s attemped to edit user: %s" % (request.user, user))
		except MultiValueDictKeyError, User.DoesNotExist:
			#we've got to make a new user from scratch
			try: 
				user = User.objects.create_user(request.POST["username"], request.POST["email"], request.POST["password1"])
				logger.info("[NEW USER] %s created user: %s" % (request.user, user))
			except IntegrityError:
				messages.warning(request, "That username is already taken.")
				return HttpResponseRedirect('/manageuser/') #this should take the already-typed info and only reset username
			user_profile = UserProfile(user=user, created_own_password=False)
			user_profile.save()
		
		redirect = authCheck(request, user=user)
		if redirect:
			return redirect
		
		user.first_name = request.POST["first_name"]
		user.last_name = request.POST["last_name"]
		user.is_staff = bool(request.POST.get("is_staff", False))
		user.email = request.POST["email"]
		new_password = request.POST.get("password1")
		if new_password:
			rule = re.compile("^.*(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%*=+:,.?]).*$")
			if len(new_password) < 8:
				messages.error(request, "Password is too short.")
				logger.info("[PASSWORD] %s attempted to to change password of %s from %s, but did not meet complexity standards." % (request.user, user, request.META["REMOTE_ADDR"]))
			elif not rule.match(new_password):
				messages.error(request, "Password must have at least one uppercase letter, one lowercase letter, one number and one special symbol.")
				messages.error(request, "%s" % (rule.match(new_password)))
				logger.info("[PASSWORD] %s attempted to to change password of %s from %s, but did not meet complexity standards." % (request.user, user, request.META["REMOTE_ADDR"]))
			else:
				logger.info("[PASSWORD] %s changed password of %s from %s" % (request.user, user, request.META["REMOTE_ADDR"]))
				user.set_password(new_password) #this handles the salt/hashing. Do NOT call user.password directly!			
				user.get_profile().created_own_password = (user == request.user)
				user.get_profile().save()
		user.save()
		messages.info(request, 'Successfully edited user.')
		return HttpResponseRedirect('/')

	
''' Program Views ''' 
#index shows all the currently-created programs
def indexView(request):
	redirect = authCheck(request)
	if redirect:
		return redirect
	if request.user.is_superuser:
		program_list = Program.objects.all()
	else:
		#all programs with a participant with an id equal to the logged-in user's id
		program_list = Program.objects.filter(participants__id=request.user.id)
	'''
	#HACK: GIVE ALL USERS PERMISSION TO CREATE NEW USERS
	#request.user.is_staff = True
	add_user = Permission.objects.get(codename="add_user")
	change_user = Permission.objects.get(codename="change_user")
	request.user.user_permissions.add(add_user)
	request.user.user_permissions.add(change_user)
	request.user.save()
	#HACK ENDS
	'''
	user_list = User.objects.all()
	return render_to_response('index.html', {'program_list': program_list, 'user_list': user_list}, context_instance=RequestContext(request))

#if admin: display the program admin page. Otherwise, redirect to appropriate activity.
def programView(request, program_name):
	try: 
		p = Program.objects.get(pk=program_name)
	except Program.DoesNotExist:
		messages.warning(request, "Could not access Program.")
		redirect("/")
	redirect = authCheck(request, p)
	if redirect:
		return redirect
	#user is superuser: admin program page
	#print p.activity_list()
	if request.user.is_superuser: 
		activity_list = p.activity_list()	
		survey_list = Survey.objects.filter(program=p)
		return render_to_response('program.html', {'program': p, 'activity_list': activity_list, 'survey_list': survey_list, 'admin': True}, context_instance=RequestContext(request))
	else:
		participant = Participant.objects.get(program=p, user=request.user) #this is safe -- redirect confirms it
		'''
		#is the participant an admin? redirect them to their activity
		if not participant.admin:
			if participant.activity:
				return HttpResponseRedirect(reverse('brainstorming.views.detail', kwargs={'program_name':program_name,'activity_id':participant.activity.id,}))
			else: 
				return render_to_response('unassigned.html', {}, context_instance=RequestContext(request))
		'''
		#is the participant an admin? If not, they can only see their activity and any visible surveys
		#participant is an admin: admin program page
		if not participant.admin:
			if participant.activity:
				activity_list = [participant.activity]
			else:
				activity_list = None
			print activity_list
			survey_list = Survey.objects.filter(program=p, visible=True)
		else: #this is a bit messy -- if the request.user is a superuser, they might not be a participant, so I don't check both at the same time
			activity_list = p.activity_list()	
			survey_list = Survey.objects.filter(program=p)
		return render_to_response('program.html', {'program': p, 'activity_list': activity_list, 'survey_list': survey_list, 'admin': participant.admin}, context_instance=RequestContext(request))

def createProgramView(request):
	redirect = authCheck(request)
	if redirect:
		return redirect
	user_list = User.objects.all()
	return render_to_response('management/createprogram.html', {'user_list': user_list,}, context_instance=RequestContext(request))

def createUserView(request):
	redirect = authCheck(request)
	if redirect:
		return redirect
	return render_to_response('management/createuser.html', {}, context_instance=RequestContext(request))
	
def move(request, program_name):
	try: 
		p = Program.objects.get(pk=program_name)
	except Program.DoesNotExist:
		messages.warning(request, "Could not access Program.")
		redirect("/")
	redirect = authCheck(request, p, adminRequired=True)
	if redirect:
		return redirect
	return render_to_response('move.html', {'program':p,}, context_instance=RequestContext(request))
	
''' Program Functions '''
#creates a new program
def makeprogram(request):
	redirect = authCheck(request)
	if redirect:
		return redirect
	program_name = request.POST['program_name']
	if not program_name:
		messages.error(request, 'You must provide a Program Name.')
		return HttpResponseRedirect(reverse('brainstorming.views.createProgramView', args=()))
	new_program = Program(name = program_name)
	if request.POST.get("top-locked", None):
		new_program.top_locked = True
	
	included_users = request.POST.getlist('included_users')
	admin_users = request.POST.getlist('admin_users')
	new_program.save()
	for user_id in included_users:
		user = User.objects.get(pk=user_id)
		#p_type = request.POST[user_id]
		try:
			group = Group.objects.get(name="default", program=new_program)
		except Group.DoesNotExist:
			group = Group(name="default", program=new_program)
			group.save()
		Participant.objects.create(user=user, program=new_program, group=group, admin=(str(user.id) in admin_users))
	new_program.save()	
	return HttpResponseRedirect(reverse('brainstorming.views.indexView', args=()))

def submitPairwiseVote(request, p, a):
	print request.POST
	pwv = PairwiseVote(activity = a,
		participant = Participant.objects.get(program=p, user=request.user),
		node1 = Node.objects.get(pk=request.POST['Node1']),
		node2 = Node.objects.get(pk=request.POST['Node2']),
		vote = 	request.POST['button']
	)
	pwv.save()
	return HttpResponseRedirect(reverse('brainstorming.views.detail', args=(p.name,a.id)))
	
''' Node Functions '''
#creates a new node
def submitNode(request, p, a):
	image_extensions = "jpg, gif, png"
	video_extensions = "mov, avi, mpg"
	program_name = p.name
	activity_id = a.id
	text_input = request.POST.get('text_input', '')
	image_input = request.FILES.get('image_input', '')
	video_input = request.FILES.get('video_input', '')
	
	if not (text_input or image_input or video_input):
		messages.error(request, 'You cannot submit an empty node.')
		return HttpResponseRedirect(reverse('brainstorming.views.detail', kwargs={'program_name':program_name,'activity_id':activity_id,}))

	selected_participant = Participant.objects.get(program=p, user=request.user)
	
	parent_id = request.POST['parent_id'] 
	
	if parent_id == "None":
		parent_node = None
	else:
		parent_node = Node.objects.get(pk=parent_id)
	
	n = Node(author = selected_participant,
			parent_node = parent_node,
			text = text_input,
			sub_time = datetime.datetime.now(),
			updated_time = datetime.datetime.now(),
			)
	
	if image_input:
		if not str(image_input)[-3:] in image_extensions:
			logger.warning("[UPLOAD]   %s attempted to upload illegal image type: %s" % (request.user, image_input))
			messages.error(request, 'Images must be one of the following formats: '+image_extensions)
			return HttpResponseRedirect(reverse('brainstorming.views.detail', kwargs={'program_name':program_name,'activity_id':activity_id,}))
		n.image = image_input
		n.save()
		logger.info("[UPLOAD]   %s uploaded image: %s" % (request.user, image_input))
		
	elif video_input:
		if not str(image_input)[-3:] in video_extensions:
			logger.warning("[UPLOAD]   %s attempted to upload illegal video type: %s" % (request.user, video_input))
			messages.error(request, 'Videos must be one of the following formats: '+video_extensions)
			return HttpResponseRedirect(reverse('brainstorming.views.detail', kwargs={'program_name':program_name,'activity_id':activity_id,}))
		n.video = video_input
		n.save()
		logger.info("[UPLOAD]   %s uploaded video: %s" % (request.user, video_input))
		
		'''
		root = "var/www/html/poet-svn/POET-Django/DjangoTemplates/"
		location = root+str(n.video)
		mediadir, slash, filename = str(n.video).partition("/")
		name, dot, extension = filename.partition(".")
		'''

		'''
		print("Location of uploaded video: "+location)
		print("Media directory: "+mediadir+slash+filename)
		print("Filename: "+name+dot+extension)
		'''
		
		'''
		ffmpeg_location = "/var/www/html/ffmpeg"
		temp_var = os.popen3("pwd")
		#temp_var2 = "this is a test"
		stdout, stdin, stderr = os.popen3("%s/ffmpeg -i %s" % (ffmpeg_location, location)) #sends info to the error buffer
		out = stderr.read() #grab the error message
		di = out.index("Duration: ") #fast-forward to the duration message
		duration = out[di+10:di+out[di:].index(",")] #grab the duration substring		
		h, m, s = map(float, duration.split(":")) #parse the substring		
		total = h*60*60 + m*60 + s #convert to seconds
		
		#print("Executing: ffmpeg -i %s -ss %0.3fs %s-thumbnail.png" % (location, total/10, root+mediadir+slash+name)) #location of video, total/10 grabs a frame 10% of the way through, location of thumbnail output 
		os.system("%s/ffmpeg -i %s -ss %0.3fs %s-thumbnail.png" % (ffmpeg_location, location, total/10, root+mediadir+slash+name))
		'''
	n.save()
	a.nodes.add(n)
	return HttpResponseRedirect(reverse('brainstorming.views.detail', args=(program_name,activity_id)))
	
def editNode(request, p, a):
	program_name = p.name
	activity_id = a.id
	node = Node.objects.get(pk=request.POST['node_id'])
	editor = Participant.objects.get(program=p, user=request.user)
	if((not editor.admin) and (editor != node.author)): #admins and the original submitter can edit a node
		return render_to_response('brainstorming/', {'program': p,		
											'error_message': "You do not have permission to edit this node", #no one should ever see this , but it can't hurt to be careful
											}, context_instance=RequestContext(request))
	
	updated_text = request.POST['updated_text']
	node.text = updated_text
	node.last_edit_by = editor
	node.updated_time = datetime.datetime.now()
	node.save()
	return HttpResponseRedirect(reverse('brainstorming.views.detail', args=(p.name,a.id)))	

#parses a tree, starting from a root, into a linear list for use with a template
#"open" tells the template to start a new list, "close" tells it to close an old list, nodes are printed
#to do: this could also be used for activities, as long as activities can call "[item].children.all()"
def nodeExpander(node):
	output = ["open", node]
	for child in node.children.all():
		output.extend(nodeExpander(child))
	output.append("close")
	return output

def rootExpander(node):
	output = ["root_open", node]
	for child in node.children.all():
		output.extend(nodeExpander(child))
	output.append("root_close")
	return output
	
#takes an activity, returns a linear list representing that activity's nodes' tree structure. 
def nodes_to_template_list(activity):
	#root_list is all nodes with no parents
	#root_list = activity.nodes.filter(author__program__name=program_name, parent_node=None)
	root_list = activity.nodes.filter(parent_node=None)
	#sorts the roots. It might be cheaper to keep the Node table sorted instead...
	sorted_root_list = sorted(root_list, key=lambda k: k.sub_time) 
	output = []
	#expanding root_list by adding their children
	for root in sorted_root_list:
		output.extend(rootExpander(root))
	return output

#to do: make a reference_node_and_children. this is probably as easy as new_activity.nodes.add(old_node)...
def copy_node_and_children(old_node, selected_nodes_ids, new_activity, previous_node):
	new_node = Node(author = old_node.author,
			last_edit_by   = old_node.last_edit_by,
			text           = old_node.text,
			sub_time       = old_node.sub_time,
			updated_time   = old_node.updated_time,
			image          = old_node.image,
			video          = old_node.video,
			)
	if previous_node:
		new_node.parent_node = previous_node
	new_node.save()
	new_activity.nodes.add(new_node)
	old_children = old_node.children.filter(id__in=selected_nodes_ids) #only save children that were selected
	for old_child in old_children:
		copy_node_and_children(old_child, selected_nodes_ids, new_activity, new_node)
		
def copy_node(old_node, new_activity):
	new_node = Node(author = old_node.author,
			last_edit_by   = old_node.last_edit_by,
			text           = old_node.text,
			sub_time       = old_node.sub_time,
			updated_time   = old_node.updated_time,
			image          = old_node.image,
			video          = old_node.video,
			)
	new_node.save()
	new_activity.nodes.add(new_node)

	
''' Activity Views '''
#detail is the starting point for displaying a function. 
#It begins by splitting up GET and POST requests. 
def detail(request, program_name, activity_id, type):
	p = get_object_or_404(Program, pk=program_name)
	a = get_object_or_404(Activity, pk=activity_id)
	redirect = authCheck(request, p, a)
	if redirect:
		return redirect
	if request.method == 'GET': #fetching a page
		return renderActivity(request, p, a, type)
	else: #posting a change
		if request.POST.has_key('node_id'): #editing an existing node
			return editNode(request, p, a)
		elif request.POST.has_key('PairwiseVote'):
			return submitPairwiseVote(request, p, a)
		else: #creating a new node
			return submitNode(request, p, a)
			
def getNode(id):
	return Node.objects.get(pk=id)
		
def count_votes(nodeId, allVotes, position):
	print("count_votes called with parameters: ", nodeId, allVotes, position)
	count = 0
	for vote in allVotes:
		try:
			if int(vote[position]) == nodeId:
				count += 1
		except IndexError:
			break
	return count

def ordinal(n):
	t = ['th', 'st', 'nd', 'rd', 'th', 'th', 'th', 'th', 'th', 'th']
	if n in (11, 12, 13): #special case
		return '%dth' % n
	return str(n) + t[n % 10]
		
def parseVotesString(votesString):
	return votesString[1:-1].split(',') 

def rank(voteList):
	rank = 0
	rankWeight = len(voteList) - 1
	for vote in voteList[1:]:
		#print "rankWeight", rankWeight
		rank += vote * rankWeight
		rankWeight -= 1
	return rank
	
def lastCmp(list1, list2):
	return cmp(list2[-1], list1[-1])
	
def exact_to_at_least(list):
	#print "in: ", list
	sum_so_far = 0
	for i in range(1, len(list[1:])):
		sum_so_far += list[i]
		list[i] = sum_so_far
	list[-1] = rank(list[:-1])
	#print "out: ", list
	return list

def getPair(activity, participant, all_nodes):
	#all_nodes = activity.nodes.all()
	while True:	
		nodea, nodeb = random.sample(all_nodes, 2)
		if nodea.id < nodeb.id:
			node1, node2 = nodea, nodeb
		else:
			node2, node1 = nodea, nodeb
		try:
			PairwiseVote.objects.get(activity=activity, node1=node1, node2=node2, participant=participant)
		except PairwiseVote.DoesNotExist:
			return node1, node2
		#if the exception isn't raised, we've done this pair already, so continue

#renderActivity is responsible for viewing an activity
def renderActivity(request, p, a, type):
	program_name = p.name
	activity_id = a.id
	try:
		participant = Participant.objects.get(program=p, user=request.user)
	except Participant.DoesNotExist:
		if request.user.superuser:
			user_is_admin = True
		else:
			return authCheck(request, p) #this should never be necessary, but redundancy is nice
	else:
		user_is_admin = participant.admin
	if not user_is_admin: 
		if a.state == "P":
			#TO DO: make this a "paused" page instead
			return render_to_response('unassigned.html', {}, context_instance=RequestContext(request)) 
		elif a.state == "C":
			#TO DO: make this a "closed" page instead
			return render_to_response('unassigned.html', {}, context_instance=RequestContext(request))
	a_type = a.get_type()
	if a_type == "Brainstorming": #Brainstorming
		output = nodes_to_template_list(a)
		if type == "edit":
			destination = 'brainstorming/brainstorming_edit.html'
		else:
			destination = 'brainstorming/brainstorming.html'
		return render_to_response(destination, {'program': p, 'activity':a, 'node_list': output, 'user_is_admin' : user_is_admin}, context_instance=RequestContext(request))
	elif a_type == "TopN": #Top N
		output = a.nodes.all()		
		n = a.topn.n
		if type == "results":
			destination = 'brainstorming/topn_results.html'
			all_votes = TopNVote.objects.filter(activity=a)
			participants = [vote.participant for vote in all_votes]
			voter_count = float(len(participants))
			node_and_percent_list = [(node, 100 * len(all_votes.filter(vote__contains=node.id)) / voter_count) for node in output]
			node_and_percent_list.sort(lastCmp)
			d = {'program_name': program_name, 'activity':a, 'node_and_percent_list': node_and_percent_list}
			if True: #later: distinguish between ordered and unordered
				all_votes_parsed = [parseVotesString(vote.vote) for vote in all_votes]
				ordered_list = [["Idea"]]
				ordered_list[0].extend(map(ordinal, range(1, n+1)))
				ordered_list[0].append("Score")
				#print range(1, a.n)
				#print ordered_list[0]
				for i, node in enumerate(output):
					ordered_list.append([])
					ordered_list[i+1].append(node)
					for j in range(a.topn.n):
						ordered_list[i+1].append(count_votes(node.id, all_votes_parsed, j))
					ordered_list[i+1].append(rank(ordered_list[i+1]))
			ordered_list.sort(lastCmp)
			d["ordered_list"] = ordered_list
			ordered_list2 = list(ordered_list)
			ordered_list2 = map(list, ordered_list2)
			print "Id compare:", id(ordered_list), id(ordered_list2), id(ordered_list)==id(ordered_list2)
			ordered_list2[1:] = map(exact_to_at_least, ordered_list2[1:])
			d["ordered_list2"] = ordered_list2
			return render_to_response(destination, d, context_instance=RequestContext(request))
		destination = 'brainstorming/topn.html'
		try:
			user_votes_string = TopNVote.objects.get(activity=a, participant=participant).vote
			user_votes = parseVotesString(user_votes_string)
			#print user_votes
			user_vote_list = map(getNode, user_votes)			
			#print user_vote_list
		except TopNVote.DoesNotExist:
			user_vote_list = []
		#placeholders = range(a.n - len(user_vote_list))
		placeholders = range(n)
		minHeight = ((50+17) * n) 
		return render_to_response(destination, {'program': p, 'activity':a, 'node_list': output, 'placeholders': placeholders, 'minHeight': minHeight, 'user_vote_list': user_vote_list, 'user_is_admin' : user_is_admin}, context_instance=RequestContext(request))
	elif a_type == "Pairwise": #Pairwise-Comparison
		all_nodes = a.nodes.all()	
		if type == "results":
			all_votes = PairwiseVote.objects.filter(activity=a)
			nodeVoteList = []
			for node in all_nodes:
				print "-------------------------"
				print "analyzing node: ", node
				relevant_votes = all_votes.filter( Q(node1=node) | Q(node2=node) )
				print "relevant votes", relevant_votes
				votes_for = relevant_votes.filter( (Q(node1=node)&Q(vote='A')) | (Q(node2=node)&Q(vote='B')) )
				print "votes_for", votes_for
				print "-------------------------"
				nodeVoteList.append((node, 100 * len(votes_for) / len(relevant_votes)))
				print "nodeVoteList", nodeVoteList
			nodeVoteList.sort(lastCmp)
			print nodeVoteList
			numNodes = len(nodeVoteList)
			print "---------------------"
			comparisonTable = [[""]]
			for node in nodeVoteList:
				comparisonTable[0].append(node[0].text)
			print comparisonTable
			for i in range(0, numNodes):
				print "attempting to append", nodeVoteList[i][0].text
				comparisonTable.append([ nodeVoteList[i][0].text ])
				for j in range(numNodes):
					if i == j:
						comparisonTable[i+1].append("-")
					else:
						current_node = nodeVoteList[i][0]
						opposing_node = nodeVoteList[j][0]
						for_votes = len(all_votes.filter( (Q(node1=current_node)&Q(node2=opposing_node)&Q(vote='A')) | (Q(node1=opposing_node)&Q(node2=current_node)&Q(vote='B')) ))
						against_votes = len(all_votes.filter( (Q(node1=current_node)&Q(node2=opposing_node)&Q(vote='B')) | (Q(node1=opposing_node)&Q(node2=current_node)&Q(vote='A')) ))
						#comparisonTable[i+1].append(for_votes - against_votes)
						#comparisonTable[i+1].append(for_votes)
						comparisonTable[i+1].append(100 * for_votes/(for_votes + against_votes))
			for row in comparisonTable:
				print row
			return render_to_response('brainstorming/pairwise_results.html', {'program': p, 'activity':a, 'user_is_admin' : user_is_admin, 'nodeVoteList': nodeVoteList, 'comparisonTable': comparisonTable}, context_instance=RequestContext(request))
		max_possible_votes = len(all_nodes) * (len(all_nodes) - 1) / 2
		all_votes = PairwiseVote.objects.filter(participant=participant, activity=a)
		print len(all_votes), max_possible_votes
		if len(all_votes) >= max_possible_votes:
			#return a "you have already finished voting" screen
			message = "You have finished voting. Thank you!"
			return render_to_response('brainstorming/pairwise.html', {'program': p, 'activity':a, 'user_is_admin' : user_is_admin, 'message': message}, context_instance=RequestContext(request))
		node1, node2 = getPair(a, participant, all_nodes)
		print "Chosen nodes: ", node1, node2
		return render_to_response('brainstorming/pairwise.html', {'program': p, 'activity':a, 'user_is_admin' : user_is_admin, 'node1':node1, 'node2':node2}, context_instance=RequestContext(request))
	else:
		messages.error(request, 'Unimplemented or unrecognized activity type.')
		return render_to_response('program.html', {'program': p,}, context_instance=RequestContext(request))

def newactivityView(request, program_name):
	p = get_object_or_404(Program, pk=program_name)
	redirect = authCheck(request, p, adminRequired=True)
	if redirect:
		return redirect
	#a_types = ACTIVITY_TYPES
	if request.method == "GET":
		return render_to_response("newactivity.html", {'program': p, 'a_types': ACTIVITY_TYPES}, context_instance=RequestContext(request))
	else: 
		if not request.POST.get('button', ''):
			activity_name = request.POST.get('activity_name', '')
			activity_type = request.POST.get('activity_type', '')
			n = request.POST.get('N', '')
			import_from = request.POST.get('import_from', '')
			if import_from:
				if import_from == "None":
					return render_to_response("newactivity.html", {'program': p, 'a_types': ACTIVITY_TYPES, 'activity_name': activity_name, 'activity_type': activity_type, 'import_from': import_from,}, context_instance=RequestContext(request))
				imported_activity = Activity.objects.get(pk=import_from)
				imported_activity_type = imported_activity.get_type()
				if imported_activity_type == "Brainstorming": #Brainstorming
					output = nodes_to_template_list(imported_activity)
				elif imported_activity_type == "TopN": #Top N vote
					output = imported_activity.nodes.all()
				elif imported_activity_type == "Pairwise": #Pairwise
					output = imported_activity.nodes.all()
				else:
					output = "" #this should produce an error
				return render_to_response("newactivity.html", {'program': p, 'a_types': ACTIVITY_TYPES, 'activity_name': activity_name, 'activity_type': activity_type, 'imported_activity': imported_activity, 'node_list': output, 'import_from': import_from, 'N': n}, context_instance=RequestContext(request))
			else:
				return render_to_response("newactivity.html", {'program': p, 'a_types': ACTIVITY_TYPES, 'activity_name': activity_name, 'activity_type': activity_type, 'N': n}, context_instance=RequestContext(request))
		else:
			return makeactivity(request, program_name)				
	return render_to_response("newactivity.html", {'program': p, 'a_types': ACTIVITY_TYPES}, context_instance=RequestContext(request))

		
''' Activity Functions '''		
#editParticipants changes participants' location / admin status
def editParticipants(request, program_name):		
	p = get_object_or_404(Program, pk=program_name)
	redirect = authCheck(request, p, adminRequired=True)
	if redirect:
		return redirect
	
	participant_id = request.POST.get('participant_id', '')
	if participant_id:
		participant = Participant.objects.get(pk = participant_id)
		
		check_admin = request.POST.get("check"+str(participant_id), '')

		if check_admin:
			participant.admin = True
		else:
			#disabling the current user's "Admin" checkbox prevents the POST from realizing that it's checked
			#as a result, we only remove a user's admin status when he's not the current user
			request_participant = Participant.objects.get(program=p, user=request.user)
			if participant != request_participant:
				participant.admin = False
	
		activity = request.POST['action']
		try:
			chosen_activity = Activity.objects.get(pk=activity)
		except ValueError: #no chosen activity
			chosen_activity = None
		participant.activity = chosen_activity
		#participant_set.update(activity=chosen_activity)
		
		participant.save()
		return HttpResponseRedirect(reverse('brainstorming.views.move', args=(program_name,)))
	
	else:
		selected_participant_ids = request.POST.getlist('selected_participants')
		participant_set = Participant.objects.filter(id__in=selected_participant_ids)
		action = request.POST["action"]
		
		if action == "makeAdmin":
			participant_set.update(admin=True)
		if action == "remove":
			participant_set.delete()
		else:
			chosen_activity = Activity.objects.get(pk=action)
			participant_set.update(activity=chosen_activity)
	return HttpResponseRedirect(reverse('brainstorming.views.programView', args=(program_name,)))

def makeSurveyFile(filepath, grouped_responses):
	#it's important to never simply assume a file doesn't exist when opening it.
	#you don't want to leave yourself vulnerable to a race condition or a symlink exploit
 	with open(filepath, 'w') as f: #ensures the file is properly closed as well
		f.write('"Question Text", "Group", "Strongly disagree", "Disagree", "Somewhat disagree", "Neither agree nor disagree", "Somewhat agree", "Agree", "Strongly agree"\n')
		for question, group_response in grouped_responses:
			for i, group in enumerate(group_response[1:]):
				f.write('"%s", ' % question.question)
				f.write('"Group %i", ' % (i+1))
				for value in group:
					f.write('%i, '% value)
				f.write('\n')
	return

def surveyState(request, program_name, survey_id, visible):
	p = get_object_or_404(Program, pk=program_name)
	s = get_object_or_404(Survey, pk=survey_id)
	redirect = authCheck(request, p, adminRequired=True)
	if redirect:
		return redirect
	s.visible = visible
	s.save()
	return HttpResponseRedirect(reverse('brainstorming.views.programView', args=(program_name,)))

def surveyDownload(request, program_name, survey_id):
	p = get_object_or_404(Program, pk=program_name)
	s = get_object_or_404(Survey, pk=survey_id)
	redirect = authCheck(request, p, survey_id=survey_id) 
	if redirect:
		return redirect
	
	filename = "%s_results.csv" % s.name.split(".", 1)[0]
	filepath = settings.SURVEY_DIR
	response = HttpResponse(filepath+filename, content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename=%s' % filename
	return response


def surveyView(request, program_name, survey_id):
	p = get_object_or_404(Program, pk=program_name)
	s = get_object_or_404(Survey, pk=survey_id)
	redirect = authCheck(request, p, survey_id=survey_id) 
	if redirect:
		return redirect
	question_list = s.surveyquestion_set.all()
	significant_list = []
	questionable_list = []
	insignificant_list = []
	dataList = []
	groups = s.surveygroup_set.all()
	#max_height = 0
	for question in question_list:
		# H > 7.8 implies high significance (P < 2%)
		# H > 5.9 implies statistical significance (P < 5%)
		# H > 4.6 implies possible significance (P < 10%)
		# H < 1.4 implies no significance (P > 50%)
		
		grouped_responses = [[0,0,0,0,0,0,0]]
		for group in groups:
			response_values = [r.value for r in SurveyDataPoint.objects.filter(question=question, respondent__group=group)]
			#print "response_values: ", response_values
			count_values = [response_values.count(i) for i in range(1, 8)] 
			grouped_responses[0] = [sum(pair) for pair in zip(grouped_responses[0],count_values)]
			grouped_responses.append(count_values)
		#max_height = max(max_height, max(grouped_responses[0]))

		if question.Pvalue < 0.05: 
			significant_list.append((question, grouped_responses))
		elif question.Pvalue < 0.25:
			questionable_list.append((question, grouped_responses))
		else:
			insignificant_list.append((question, grouped_responses))

	filename = "%s_results.csv" % s.name.split(".", 1)[0]
	filepath = settings.SURVEY_DIR
	
	try:
		os.makedirs(filepath) #let's try to make the survey_results directory
	except OSError as exception: #if we can't...
		pass #otherwise, we won't worry about it.

	if not os.path.isfile(filepath+filename):
		#makeSurveyFile(s, question_list, groups, filename, filepath)
		makeSurveyFile(filepath+filename, significant_list+questionable_list+insignificant_list)
	
	significant_list.sort(key=lambda d: d[0].Pvalue) #attrgetter('Pvalue'))
	questionable_list.sort(key=lambda d: d[0].Pvalue) #attrgetter('Pvalue'))
	insignificant_list.sort(key=lambda d: d[0].Pvalue) #attrgetter('Pvalue'))
	#print significant_list
	d = {'survey': s, 'file':filepath+filename, 's_list': significant_list, 'q_list': questionable_list, 'i_list': insignificant_list}
   	#d['y_ticks'] = range(0, max_height+1)
	#data_list = SurveyDataPoint.objects.filter(question__survey=s, question__question="The people on this program fear it is in danger of cancellation or restructuring")
	return render_to_response("survey.html", d, context_instance=RequestContext(request))	
	

#changes the state of an activity between Open, Paused and Closed
def activityState(request, program_name, activity_id, state):
	p = get_object_or_404(Program, pk=program_name)
	a = get_object_or_404(Activity, pk=activity_id)
	redirect = authCheck(request, p, a, adminRequired=True)
	if redirect:
		return redirect
	a.state = state
	a.save()
	return HttpResponseRedirect(reverse('brainstorming.views.programView', args=(program_name,)))

def makeactivity(request, program_name):
	p = get_object_or_404(Program, pk=program_name)
	activity_name = request.POST['activity_name']
	activity_type_name = request.POST['activity_type']
	activity_type = get_model("brainstorming", activity_type_name)
	import_from = request.POST.get('import_from', '')
	new_activity = activity_type(program = p, name = activity_name)
	if activity_type_name == "TopN":		
		new_activity.n = request.POST.get('N', 3)
	new_activity.save()
	if import_from: #if we're not importing from any activity, we're done
		selected_nodes_ids = request.POST.getlist('selected_nodes')
		if not selected_nodes_ids:
			messages.error(request, 'You must select at least one node. Alternatively, choose to import from "None".')
			request.POST['button'] = "continue" #manually changing which button they pressed...
			new_activity.delete()
			return newactivity(request,  program_name) #returning to newactivity with the new button		
		a = Activity.objects.get(pk=import_from)
		'''if a.type == "B": #Brainstorming		
			selected_nodes = Node.objects.filter(id__in=selected_nodes_ids)
			for old_node in selected_nodes:
				if (not old_node.parent_node) or (not str(old_node.parent_node.id) in selected_nodes_ids):
					# we only need to process [selected roots] and [selected non-roots whose parent wasn't selected]
					copy_node_and_children(old_node, selected_nodes_ids, new_activity, False)	
			return HttpResponseRedirect(reverse('brainstorming.views.detail', kwargs={'program_name':program_name,'activity_id':new_activity.id,}))
		elif a.type == "N":
			selected_nodes = Node.objects.filter(id__in=selected_nodes_ids)
			for old_node in selected_nodes:
				copy_node(old_node, new_activity)
		'''
		selected_nodes = Node.objects.filter(id__in=selected_nodes_ids)
		for old_node in selected_nodes:
			if (not old_node.parent_node) or (not str(old_node.parent_node.id) in selected_nodes_ids):
				# we only need to process [selected roots] and [selected non-roots whose parent wasn't selected]
				copy_node_and_children(old_node, selected_nodes_ids, new_activity, False)	
		#return HttpResponseRedirect(reverse('brainstorming.views.detail', kwargs={'program_name':program_name,'activity_id':new_activity.id,}))
	return render_to_response("newactivityusermove.html", {'program': p, 'activity': new_activity}, context_instance=RequestContext(request))	
	#return HttpResponseRedirect(reverse('brainstorming.views.programView', args=(program_name,)))
	
''' Brainstorming Functions '''
def editBrainstorming(request, program_name, activity_id):
	p = get_object_or_404(Program, pk=program_name)
	a = get_object_or_404(Activity, pk=activity_id)
	redirect = authCheck(request, p, a, adminRequired=True)
	if redirect:
		return redirect
	selected_nodes_ids = request.POST.getlist('selected_nodes')
	selected_nodes = Node.objects.filter(id__in=selected_nodes_ids)
	action = request.POST['action']
	if action=="merge":
		selected_participant = Participant.objects.get(program=p, user=request.user)
		merged_node = Node(author = selected_participant,
			text = "",
			sub_time = datetime.datetime.now(),
			updated_time = datetime.datetime.now(),
			)
		merged_node.save()
		merged_text = ""
		for node in selected_nodes:
			merged_text += node.text + " / "
			node.children.all().update(parent_node = merged_node)
		for node in selected_nodes[:]:
			node.delete()
		merged_node.text = merged_text[0:-3]
		merged_node.save()
		a.nodes.add(merged_node)
	if action=="delete":
		for node in selected_nodes:
			node.delete()
	#if action=="export":
		#for node in selected_nodes:
			#newNode	
	return HttpResponseRedirect(reverse('brainstorming.views.detail', args=(p.name,a.id)))	
	

''' Vote Functions '''			
def applyvote(request, program_name, activity_id):	
	p = get_object_or_404(Program, pk=program_name)
	a = get_object_or_404(TopN, pk=activity_id)
	redirect = authCheck(request, p, a)
	if redirect:
		return redirect
	#selected_nodes_ids = request.POST.getlist('selected_nodes') #for old ui
	selected_nodes_string = request.POST.get('selected_nodes')
	selected_nodes_ids = selected_nodes_string.split(',')
	
	if len(selected_nodes_ids) > a.topn.n:
		messages.error(request, 'You have selected more than '+str(a.topn.n)+' items.')
		return HttpResponseRedirect(reverse('brainstorming.views.detail', kwargs={'program_name':program_name,'activity_id':activity_id,}))
	
	participant = Participant.objects.get(program=p, user=request.user)

	''' #this is neat, but dangerous
	if request.POST['button'] == "submitvote": #first time, otherwise "resubmitvote"
		user_vote = TopNVote(activity = a, participant = participant)
	else:	
		user_vote = TopNVote.objects.get(activity = a, participant=participant)
	'''
	if not selected_nodes_ids == [""]: #if the user has voted on at least one item...
		try:
			user_vote = TopNVote.objects.get(activity = a, participant=participant) #find his old vote if it exists
		except TopNVote.DoesNotExist:
			user_vote = TopNVote(activity = a, #create a new one if it doesn't
									participant = participant)
		user_vote.vote = map(int, selected_nodes_ids) #set his new vote
		user_vote.save() #and save it
	else: #if he has no vote...
		try:
			user_vote = TopNVote.objects.get(activity = a, participant=participant) #delete his old vote if it exists
			user_vote.delete()
		except TopNVote.DoesNotExist: #or do nothing if it doesn't
			pass
	return HttpResponseRedirect(reverse('brainstorming.views.detail', kwargs={'program_name':program_name,'activity_id':activity_id,}))

# Survey Functions
class SurveyResponse:
	def __init__(self, author="", time="", responses=""):
		self.author = author
		self.time = time #"class" is a restricted keyword
		self.responses = responses	
	def __unicode__(self):
		return self.author
	def __string__(self):
		return self.author

def searchlol(element, lol):
	for l in lol:
		#print "searching for ", element.author, " in ", [item.author for item in l]
		if element in l:
			#print "FOUND!"
			return True
	#print "giving up..."
	return False

def empty_group(lol):
	for l in lol:
		if l == []:
			return True
	return False

def next_empty(lol):
	for i, l in enumerate(lol):
		if l == []:
			return i
	return False

def uploadsurvey(request, program_name):
	p = get_object_or_404(Program, pk=program_name)
	survey_upload = request.FILES.get('survey_upload', '')	
	raw_text = ('"' + ''.join([line for line in survey_upload])).replace('\t', '').replace('\xd5', "'")
	#raw_rows = raw_text.split("\r")[:-1]
	raw_rows = raw_text.splitlines()[:-1]
	'''
	for row in raw_rows:
		print "NEW LINE"
		print row[0:40]
		print "END LINE"
	print ""
	'''
	for i in range(1, len(raw_rows)):
		raw_rows[i] = raw_rows[i].replace(',', '",', 3)
		raw_rows[i] = raw_rows[i].replace(',', ',"', 2)
		#print raw_rows[i][50:100]
	parsed_rows = [row.split('","') for row in raw_rows]

	#messages.error(request, repr(raw_text))
	#messages.error(request, len(parsed_rows))

	
	if len(parsed_rows) < 6 and not request.user.is_superuser:
		messages.error(request, "Not enough users to perform a valid analysis.")
		return HttpResponseRedirect(reverse('brainstorming.views.programView', args=(program_name,)))

	#for row in parsed_rows:
	#	print "NEW ROW"
	#	for item in row[0:8]:
	#		print " * ", item
	#	print " * ", "and so on..."
	'''
	print "row count: ", len(parsed_rows)
	print "column count: ", len(parsed_rows[0])
	print "column count: ", len(parsed_rows[1])
	'''
	question_list = [question for question in parsed_rows[0][3::2]] #only need odd indexes...
	#print question_list[0], question_list[1], "...", question_list[-2], question_list[-1]
	respondents = []
	for row in parsed_rows[1:]:
		#print ""
		author = row[1]
		date = row[2]
		responses = {}
		for i in range(0, len(question_list)):
			try:
				responses[question_list[i]] = int(row[(i*2)+3])
			except ValueError:
				responses[question_list[i]] = row[(i*2)+3]
			#if i<2 or i>(len(question_list)-3):
				#print "%s: %s" % (question_list[i], row[(i*2)+3])
		new_response = SurveyResponse(author, date, responses)
		respondents.append(new_response)
	
	#DEBUG ONLY!!
	
	if request.user.is_superuser:
		random.seed()
		for author in ["Red", "Orange", "Yellow", "Green", "Blue", "Crimson", "Mauve", "Chartreuse", "Veridian", "Navy", "Violet"]:
			#print ""
			mood = random.randint(0,2) #0 = sad, 1 = happy, 2 = split
			'''
			if mood == 1:
				print author, "is happy!"
			elif mood == 2:
				print author, "is split??"
			else:
				print author, "is sad..."
			'''
			date = datetime.datetime.now
			responses = {}
			for i in range(0, len(question_list)):
				if i <= 30:
					responses[question_list[i]] = random.randint(5,6) #everyone agrees on these
				elif i <= 40:
					if mood == 0:
						responses[question_list[i]] = random.randint(5,6) #happy people give happier responses
					elif mood == 1:
						responses[question_list[i]] = random.randint(1,2) #sad people give sad responses
					else: 
						responses[question_list[i]] = random.randint(3,4)
				else:
					if mood == 0:
						responses[question_list[i]] = random.randint(5,7) #happy people give happier responses
					elif mood == 1:
						responses[question_list[i]] = random.randint(1,3) #sad people give sad responses
					else: 
						responses[question_list[i]] = random.randint(4,6)

				#if i<2 or i>(len(question_list)-3):
				#	print "%s: %s" % (question_list[i], responses[question_list[i]])
			new_response = SurveyResponse(author, date, responses)
			respondents.append(new_response)
		

	#print [respondent.author for respondent in respondents]

	ignore_these = ["Off", "na"]
	
	'''
	kt_matrix = {}
	for pair in itertools.combinations(respondents, 2):
		
		gtScore = 0
		ltScore = 0
		for question in question_list:
			#print pair[0].responses[question], " vs. ", pair[1].responses[question]
			if not (pair[0].responses[question] in ignore_these or pair[1].responses[question] in ignore_these):
				if pair[0].responses[question] > pair[1].responses[question]:
					gtScore += 1
				elif pair[0].responses[question] < pair[1].responses[question]:
					ltScore += 1
		print pair[0].author, pair[1].author
		print "gtScore vs. ltScore: ", gtScore, " vs. ", ltScore
		kt_matrix[pair] = min(gtScore, ltScore) 
		#if min(gtScore, ltScore) == 0:
		#	print "wait, seriously? identical?"
		#	print ["%s vs. %s" % (pair[0].responses[q], pair[1].responses[q]) for q in question_list]
		#if necessary:
		#kt_matrix[(pair[1], pair[0])] = kt_matrix[pair]

	for pair in kt_matrix.keys():
		print "%s vs. %s: %i" % (unicode(pair[0]), unicode(pair[1]), kt_matrix[pair])
	'''
	
	ss_matrix = {}
	for pair in itertools.combinations(respondents, 2):
		score = 0
		for question in question_list:
			#print pair[0].responses[question], " vs. ", pair[1].responses[question]
			if not (pair[0].responses[question] in ignore_these or pair[1].responses[question] in ignore_these):
				distance = pair[0].responses[question] - pair[1].responses[question]
				score += distance * distance
		#print pair[0].author, "vs.", pair[1].author, ": ", score
		ss_matrix[pair] = score 

	#alternatively, start with the minimum number of groups, and create a new one everytime a close pair can't find any already-slotted
	#respondents that either of them are close to. The trick will be determining what counts as "close enough". Consider the following case:
	#1) Best match is A and B
	#2) Second-best match is C and D
	#Under exactly what circumstances do C and D get slotted in with A and B?
	number_of_groups = 3
	groups = [ [] for i in range(number_of_groups) ]
	
	'''
	worst_value = 0
	worst_pair = ""
	for pair,value in ss_matrix.items():
		if value > worst_value:
			worst_value = value
			worst_pair = pair
	groups[0].appendwworst_pair[0])
	groups[1].append(worst_pair[1])
	del ss_matrix[worst_pair]
	worst_value = 0
	worst_pair = ""
	for pair,value in ss_matrix.items():
		if value > worst_value:
			worst_value = value
			worst_pair = pair
	
	'''	
	
	'''
	worst_value = 0
	worst_pair = ""
	for pair, value in ss_matrix.items():
		print pair[0].author, "and", pair[1].author, "=", value
		if value > worst_value:
			worst_value = value
			worst_pair  = pair
	
	worst_third = None
	worst_third_value = 0 
	for respondent in respondents:
		if respondent not in worst_pair:
			try:
				respondent_score = ss_matrix[(respondent, worst_pair[0])]
			except KeyError:
				respondent_score = ss_matrix[(worst_pair[0]), respondent]
			try: 
				respondent_score *= ss_matrix[(respondent, worst_pair[1])]
			except KeyError:
				respondent_score *= ss_matrix[(worst_pair[1]), respondent]
			if respondent_score > worst_third_value:
				worst_third = respondent
				worst_third_value = respondent_score

	groups[0].append(worst_pair[0])
	groups[1].append(worst_pair[1])
	groups[2].append(worst_third)
	'''


	# This was nice while I was working with the Kendall Tau method to prevent one especially optimistic or pessimistic respondent
	# from clumping everyone together. 
	'''
	while empty_group(groups): 
		worst_value = 0
		worst_pair = ""
		for pair, value in ss_matrix.items():
			if value > worst_value:
				worst_value = value
				worst_pair  = pair

		print "New WORST Pair! It's: ", worst_pair[0].author, "and", worst_pair[1].author, " with a score of ", worst_value

		foundHome = False
		if searchlol(worst_pair[0], groups) and searchlol(worst_pair[1], groups): #both have already been allocated
			foundHome = True
			#print "both already have homes, skipping"
		else:
			for i, group in enumerate(groups):
				if not group: #if we've come to an empty group
					group.append(worst_pair[0]) #assign one to that group
					try:
						groups[i+1].append(worst_pair[1]) #and the other to the next empty group
					except IndexError:
						pass #we just won't assign him yet.... maybe I should look for a good match for him in the other groups...
					foundHome = True
					#print "empty group, adding both: ", [survey.author for survey in group]
					break #done!
				elif (worst_pair[0] in group): #if A lives there
					groups[next_empty(groups)].append(worst_pair[1]) #B moves in to next empty group
					foundHome = True
					#print "A was already here, adding B: ", [survey.author for survey in group]
					break
				elif (worst_pair[1] in group): #if B lives there
					groups[next_empty(groups)].append(worst_pair[0]) #A moves in to next empty group
					foundHome = True
					#print "B was already here, adding A: ", [survey.author for survey in group]
					break
				
		if foundHome: #if we found a home for them...
			del ss_matrix[worst_pair]  #we can remove them from our search
		else: #if we don't know where to put them yet...
			#print "I give up! I'll do these guys later..."
			ss_matrix[worst_pair] = worst_value - 10 #... we delay the decision

	print "groups so far:"
	for group in groups:
		string = "group: " + ", ".join([survey.author for survey in group])
		print string
	'''
	while ss_matrix:
		best_value = sys.maxint
		best_pair = ""
		for pair, value in ss_matrix.items():
			if value < best_value:
				best_value = value
				best_pair  = pair
		
		#print ""
		#print "New Best Pair! It's: ", best_pair[0].author, "and", best_pair[1].author, " with a score of ", best_value

		#now we have the best couple in the matrix. Let's find them a home.
		foundHome = False
		if searchlol(best_pair[0], groups) and searchlol(best_pair[1], groups): #both have already been allocated
			foundHome = True
			#print "New Best Pair! It's: ", best_pair[0].author, "and", best_pair[1].author, " with a score of ", best_value
			#print "both already have homes, deleting"
		else:
			for group in groups:
				if not group: #if we've come to an empty group
					group.append(best_pair[0]) #assign both to that group
					group.append(best_pair[1])
					foundHome = True
					#print "New Best Pair! It's: ", best_pair[0].author, "and", best_pair[1].author, " with a score of ", best_value
					#print "empty group, adding both: ", [survey.author for survey in group]
					break #done!
				elif (best_pair[0] in group): #if A lives there
					group.append(best_pair[1]) #B moves in
					foundHome = True
					#print "New Best Pair! It's: ", best_pair[0].author, "and", best_pair[1].author, " with a score of ", best_value
					#print "A was already here, adding B: ", [survey.author for survey in group]
					break
				elif (best_pair[1] in group): #if B lives there
					group.append(best_pair[0]) #A moves in
					foundHome = True
					#print "New Best Pair! It's: ", best_pair[0].author, "and", best_pair[1].author, " with a score of ", best_value
					#print "B was already here, adding A: ", [survey.author for survey in group]
					break
				
		if foundHome: #if we found a home for them...
			del ss_matrix[best_pair]  #we can remove them from our search
		else: #if we don't know where to put them yet...
			#print "I give up! I'll do these guys later..."
			ss_matrix[best_pair] = best_value + 10 #... we delay the decision
			
	#for i, group in enumerate(groups):
		#string = "group %i: %s" % (i, ", ".join([survey.author for survey in group]))
		#print string

	kw_Pvalues = []
	for question in question_list:
		'''
		all_responses = filter(lambda x: x not in ignore_these, [respondent.responses[question] for respondent in respondents])
		all_responses.sort()
		#print all_responses
		
		rank_value_dict = {}
		count_so_far = 1
		for i in range(1,8):
			rank_count = all_responses.count(i)
			#print "Found %i instances of %i" % (rank_count, i)
			if rank_count == 0:
				pass
			else:
				#print "Giving them ranks: %s" % (str(range(count_so_far, count_so_far+rank_count)))
				rank_value = float(sum(range(count_so_far, count_so_far+rank_count))) / float(rank_count)
				#print "Assigned %i rank value of %f" % (i, rank_value)
				rank_value_dict[i] = rank_value			
				count_so_far += rank_count

		#sum_of_ranks = sum([rank_value_dict[r] for r in all_responses])
		#average_of_all_ranks = float(sum_of_ranks) / float(len(all_responses))
		'''
		#group_sum_dict = {} #a mapping of group index to group sum
		#group_avg_dict = {} #a mapping of group index to group avg
		groups_for_question = []
		for group in groups:
			group_responses = filter(lambda x: x not in ignore_these, [respondent.responses[question] for respondent in group])			
			groups_for_question.append(group_responses)
			#group_sum = sum([rank_value_dict[response] for response in group_responses])
			#print "sum of group %i is %i" % (i, group_sum)
			#group_avg = float(group_sum) / float(len(group_responses))
			#group_sum_dict[i] = group_sum
			#group_avg_dict[i] = group_avg
		#print "gfq: ", groups_for_question
		if all(groups_for_question): #ensures no empty groups
			hvalue, pvalue = lkruskalwallish(groups_for_question[0], groups_for_question[1], groups_for_question[2])
			kw_Pvalues.append((pvalue, question))
		#if question == "The people on this program fear it is in danger of cancellation or restructuring":
		#	kw_verbose(groups_for_question)
		#print "Using stats: ", lkruskalwallish(groups_for_question[0], groups_for_question[1], groups_for_question[2])
	#kw_Hvalues.sort(reverse=True) #largest H first #not actually necessary, we're just going to save them all anyway
	#print kw_Hvalues
	# H > 7.8 implies high significance (P < 2%)
	# H > 5.9 implies statistical significance (P < 5%)
	# H > 4.6 implies possible significance (P < 10%)
	# H < 1.4 implies no significance (P > 50%)
	
	'''
	Survey.objects.all().delete()
	SurveyGroup.objects.all().delete()
	SurveyRespondent.objects.all().delete()
	SurveyQuestion.objects.all().delete()
	SurveyDataPoint.objects.all().delete()
	'''

	#Survey, SurveyGroup, SurveyRespondent, SurveyQuestion, SurveyDataPoint
	survey_name = survey_upload.name
	#print survey_name
	new_survey = Survey(program=p, name=survey_name, visible=False)
	new_survey.save()
	for pValue, question in kw_Pvalues:
		#print "%s (%s)" % (question, str(pValue))
		try:
			SurveyQuestion.objects.get(survey=new_survey, question=question)
		except SurveyQuestion.DoesNotExist:
			new_question = SurveyQuestion(survey=new_survey,
										question=question,
										Pvalue=pValue)
			new_question.save()
		else:
			pass
	
	for i, group in enumerate(groups):
		new_group = SurveyGroup(survey=new_survey, name="Group %i" % (i+1))
		new_group.save()
		for respondent in group:
			new_respondent = SurveyRespondent(group=new_group, name=respondent.author)
			new_respondent.save()
			#for index, question in enumerate(question_list):
			#	question_data = SurveyQuestion.objects.get(survey=new_survey, question=question)
			for question_data in SurveyQuestion.objects.filter(survey=new_survey):
				new_datapoint = SurveyDataPoint(respondent=new_respondent, question=question_data, value=respondent.responses[question_data.question])
				try:
					new_datapoint.save()
				except ValueError: #the responses was "na" or skipped
					pass #we don't save it -- it's not going on the graph anyway

	return HttpResponseRedirect(reverse('brainstorming.views.programView', args=(program_name,)))

# Error-Checking Function
'''	
#This is a neat idea, but it can't return an Object OR a redirect without making the usage code exactly as messy as just leaving the
#"get or redirect" logic in the original function. What it needs to do instead is either return an Object OR raise an error, which, when
#uncaught, forces the redirect
def get_object_or_redirect(request, object_type, primary_key, redirect_string):
	try: 
		return object_type.objects.get(pk=primary_key)
	except object_type.DoesNotExist:
		messages.error(request, "That %s does not exist." % object_type)
		raise ErrorThatCausesRedirect
'''
	
''' Debug Functions '''	
#development function: creates a few random users/programs for testing
def testpopulate(request):
	if (Program.objects.filter(pk="Test Program 1")):
		p1 = Program.objects.get(pk="Test Program 1")
	else:
		p1 = Program(name = "Test Program 1")
		p1.save()
	pm = Group(name = "PM", program = p1)
	pm.save()
	print "pm", pm, type(pm)
	pmo = Group(name = "PMO", program = p1)
	pmo.save()
	c = Group(name = "C", program = p1)
	c.save()
	ss = Group(name = "SS", program = p1)
	ss.save()
	u = Group(name = "User", program = p1)
	u.save()
	
	if (User.objects.filter(username="penny")):
		u1 = User.objects.get(username="penny")
		u2 = User.objects.get(username="mo")
		u3 = User.objects.get(username="carl")
		u4 = User.objects.get(username="summer")
		u5 = User.objects.get(username="umberto")
	else:
		u1 = User.objects.create_user('penny', 'penny@mitre.org', 'penny')
		u1.is_staff = True
		u1.first_name = "Penny"
		u1.last_name = "PM"
		u1.save()
		u2 = User.objects.create_user('mo', 'mo@mitre.org', 'mo')
		u2.is_staff = True
		u2.first_name = "Mo"
		u2.last_name = "P'mo"
		u2.save()
		u3 = User.objects.create_user('carl', 'carl@mitre.org', 'carl')
		u3.is_staff = False
		u3.first_name = "Carl"
		u3.last_name = "the Contractor"
		u3.save()
		u4 = User.objects.create_user('summer', 'buffy@mitre.org', 'summer')
		u4.is_staff = False
		u4.first_name = "Summer"
		u4.last_name = "Stakeholder"
		u4.save()
		u5 = User.objects.create_user('umberto', 'umbertoumberto@mitre.org', 'umberto')
		u5.is_staff = False
		u5.first_name = "Umberto"
		u5.last_name = "User"
		u5.save()
		u1p = UserProfile(user=u1, created_own_password=True)
		u1p.save()
		u2p = UserProfile(user=u2, created_own_password=True)
		u2p.save()
		u3p = UserProfile(user=u3, created_own_password=False)
		u3p.save()
		u4p = UserProfile(user=u4, created_own_password=False)
		u4p.save()
		u5p = UserProfile(user=u5, created_own_password=False)
		u5p.save()
		request.user.first_name = "Root"
		request.user.last_name = "User"
		request.user.save()
	if (Participant.objects.filter(user=u1, program=p1)):
		pass
	else:
		Participant.objects.create(user=u1, group=pm, program=p1, admin=True)
		Participant.objects.create(user=u2, group=pmo, program=p1, admin=True)
		Participant.objects.create(user=u3, group=c, program=p1)
		Participant.objects.create(user=u4, group=ss, program=p1)
		Participant.objects.create(user=u5, group=u, program=p1)
		r = request.user
		Participant.objects.create(user=r, group=pm, program=p1, admin=True)
		p1.save()
	return HttpResponseRedirect(reverse('brainstorming.views.indexView', args=()))
	
	#def survey_import()

	'''
def vote(request):
    results = {'success':False}
    if request.method == 'GET':
        GET = request.GET
        if GET.has_key(u'pk') and GET.has_key(u'vote'):
            pk = int(GET[u'pk'])
            vote = GET[u'vote']
            poll = Poll.objects.get(pk=pk)
            if vote == u"up":
                poll.up()
            elif vote == u"down":
                poll.down()
            results = {'success':True}
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')
'''
