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

from django.core.exceptions import MiddlewareNotUsed 
#from django.utils.http import http_date, parse_http_date_safe
from brainstorming.models import Program, Activity
from django.contrib.admin.models import LogEntry
from django.db.models import get_model
import logging		
from django.contrib import messages
from django.http import HttpResponseRedirect #, Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import MiddlewareNotUsed

#CUSTOM_LOGGERS = frozenset(["Request_Logger", "Access_Logger"])

class RedirectionAndLoggingMiddleware(object):
	#I used to disable this middleware when it couldn't find a logger, but now that it handles redirection, too, I can't afford not to use it.
	#Now, if a logger isn't properly defined, all log messages will be sent to the root logger instead. 
	'''
	def __init__(self):
		#if one of our loggers isn't defined, we disable this Middleware
		#if we didn't, the log statements would simply be passed to the root logger. That's not a critical failure, but it's sloppy.
		if not CUSTOM_LOGGERS.issubset(logging.Logger.manager.loggerDict.keys()):
			raise MiddlewareNotUsed
		pass
	'''

	def process_request(self, request): 
		request_logger = logging.getLogger('Request_Logger')
		request_logger.info("User %s (%s) requested: %s" % (request.user, request.META["REMOTE_ADDR"], request.META["PATH_INFO"]))
		if request.POST:
			if request.POST.get("action", None) == "delete_selected" and request.POST.get("post", None) == "yes":		
				#print "Delete Selected detected"
				access_logger = logging.getLogger('Access_Logger')
				request_path_items = request.META["PATH_INFO"].split("/")
				model_type = get_model("brainstorming", request_path_items[-2])
				#print "model_type", model_type
				if model_type:
					for id in request.POST.getlist('_selected_action'):
						#print "Now processing: ", id
						item = model_type.objects.get(id=id)
						#print "item: ", item
						access_logger.info("[ADMIN]    %s deleted %s: %s" % (request.user, request_path_items[-2], item))
				else:
					for id in request.POST.getlist('_selected_action'):
						#print "Now processing: ", id
						#item = model_type.objects.get(id=id)
						#print "item: ", item
						access_logger.info("[ADMIN]    %s deleted %s: %s" % (request.user, request_path_items[-2], id))
		return False

	def process_view(self, request, view_func, view_args, view_kwargs):
		#print "VIEW: ", view_func.func_name, "ARGS: ", view_args, "KWARGS: ", view_kwargs
		access_logger = logging.getLogger('Access_Logger')
		if "program_name" in view_kwargs.keys():
			try:
				p = Program.objects.get(pk=view_kwargs["program_name"])
			except Program.DoesNotExist:
				messages.error(request, "Program does not exist.")
				access_logger.warning("[ACCESS]   USER: %s REQUEST: %s RESULT: Redirecting to index. REASON: Program does not exist." % (request.user, request.path))
				return HttpResponseRedirect("/")					
			if "activity_id" in view_kwargs.keys():
				try:
					a = Activity.objects.get(pk=view_kwargs["activity_id"])
				except Activity.DoesNotExist:
					messages.error(request, "Activity does not exist.")
					access_logger.warning("[ACCESS]   USER: %s REQUEST: %s RESULT: Redirecting to program index. REASON: Activity does not exist." % (request.user, request.path))
					return HttpResponseRedirect(reverse('brainstorming.views.programView', args=(view_kwargs["program_name"],)))
				if a.program != p:
					messages.error(request, "That activity does not belong to that program.")
					access_logger.warning("[ACCESS]   USER: %s REQUEST: %s RESULT: Redirecting to program index. REASON: Activity does not belong to that program." % (request.user, request.path))
					return HttpResponseRedirect(reverse('brainstorming.views.programView', args=(view_kwargs["program_name"],)))
		#print "VIEW ATTR: ", dir(view_func)
		return None

		
	def process_response(self, request, response):
		access_logger = logging.getLogger('Access_Logger')
		request_path_items = request.META["PATH_INFO"].split("/")
		#print "request_path_split: ", request_path_items
		if request.POST:
			#print "This is a POST: ", request.POST
			if request_path_items[1] == "admin":
				if request.POST.get("_save", None):
					#print "FOUND SAVE:"
					last_log = LogEntry.objects.latest('id') 
					#print (last_log.user, last_log.object_repr, last_log.change_message)
					#print "request_path_split: ", request_path_items
					if last_log.change_message:
						access_logger.info("[ADMIN]    %s edited %s: %s" % (last_log.user, last_log.object_repr, last_log.change_message))
					else:
						access_logger.info("[ADMIN]    %s added %s: %s" % (last_log.user, request_path_items[-3], last_log.object_repr))
					
				elif not request.POST.get("action", None) == "delete_selected":
					last_log = LogEntry.objects.latest('id') 
					if request_path_items[-2] == "add":
						access_logger.info("[ADMIN]    %s added %s: %s" % (request.user, request_path_items[-3], last_log.object_repr))
					elif request_path_items[-2] == "delete":
						access_logger.info("[ADMIN]    %s deleted %s: %s" % (request.user, request_path_items[-4], last_log.object_repr))
					else:
						access_logger.info("[ADMIN]    %s edited %s: %s" % (last_log.user, last_log.object_repr, last_log.change_message))
		return response
