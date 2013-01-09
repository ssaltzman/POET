'''
Approved for Public Release: 12-3351. Distribution Unlimited
			(c)2012-The MITRE Corporation. 
Licensed under the Apache License, Version 2.0 (the "License");
			you may not use this file except in compliance with the License.
			You may obtain a copy of the License at
				http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

'''

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
admin.autodiscover()                                               
from brainstorming.forms import ValidatingPasswordChangeForm

urlpatterns = patterns('',
	#this includes all the urls in admin.site.urls, treating admin/ as its root
	(r'^change_password/$', 'django.contrib.auth.views.password_change',
		{'password_change_form': ValidatingPasswordChangeForm}), #hijacking the password_change form on the admin site -- this is the right way to do this
	(r'^admin/auth/user/(?P<user_id>\d+)/password/', 'brainstorming.views.manageuser'), #until I can figure out how to override the user_change_password form, I'll just hijack that view
    url(r'^admin/', include(admin.site.urls)),
	
	(r'^change-password-done/$', 'django.contrib.auth.views.password_change_done'),
)

urlpatterns += patterns('brainstorming.views',
	(r'^$', 'indexView'),       #program list
	(r'^index/$', 'indexView'), #program list
	
#	(r'^user_settings/$', 'userSettingsView'),
	
	
	(r'^createprogram/$', 'createProgramView'),
	(r'^makeprogram/$', 'makeprogram'),
#	(r'^createuser/$', 'createUserView'),
	(r'^newuser/$',    'manageuser', {'user_id': None}),
	(r'^manageuser/$', 'manageuser', {'user_id': None}),
	(r'^manageuser/(?P<user_id>\d+)/$', 'manageuser'), 
	
	(r'^login/$', 'login'),		
	(r'^logout/$', 'logout'),	
	
	(r'^testpopulate/$', 'testpopulate'), #program list
	
#	(r'^(\w*)/login/$', 'django.contrib.auth.views.login'),	
#	(r'^(?P<next>(\w*))/login/$', 'django.contrib.auth.views.login'),
#	(r'^index/login/$', 'django.contrib.auth.views.login'),
	
	(r'^(?P<program_name>(\w+\s*)+)/move/$', 'move'), 
	(r'^(?P<program_name>(\w+\s*)+)/editParticipants/$', 'editParticipants'), 
	(r'^(?P<program_name>(\w+\s*)+)/newactivity/$', 'newactivityView'), #create a new activity
	(r'^(?P<program_name>(\w+\s*)+)/uploadsurvey/$', 'uploadsurvey'), #upload survey data
	(r'^(?P<program_name>(\w+\s*)+)/$', 'programView'), #view a particular program's ideas
	
	(r'^(?P<program_name>(\w+\s*)+)/survey/(?P<survey_id>\d+)/visible/$',   'surveyState', {'visible': True}),
	(r'^(?P<program_name>(\w+\s*)+)/survey/(?P<survey_id>\d+)/invisible/$', 'surveyState', {'visible': False}),
	(r'^(?P<program_name>(\w+\s*)+)/survey/(?P<survey_id>\d+)/download/$', 'surveyDownload'),
	(r'^(?P<program_name>(\w+\s*)+)/survey/(?P<survey_id>\d+)/$', 'surveyView'),

	(r'^(?P<program_name>(\w+\s*)+)/(?P<activity_id>\d+)/open/$', 'activityState', {'state': 'O'}),
	(r'^(?P<program_name>(\w+\s*)+)/(?P<activity_id>\d+)/pause/$', 'activityState', {'state': 'P'}),
	(r'^(?P<program_name>(\w+\s*)+)/(?P<activity_id>\d+)/close/$', 'activityState', {'state': 'C'}),
	
	(r'^(?P<program_name>(\w+\s*)+)/(?P<activity_id>\d+)/edit/$', 'detail', {'type': 'edit'}),
	(r'^(?P<program_name>(\w+\s*)+)/(?P<activity_id>\d+)/applyvote/$', 'applyvote'),
	(r'^(?P<program_name>(\w+\s*)+)/(?P<activity_id>\d+)/editBrainstorming/$', 'editBrainstorming'),
	(r'^(?P<program_name>(\w+\s*)+)/(?P<activity_id>\d+)/results/$', 'detail', {'type': 'results'}),
	(r'^(?P<program_name>(\w+\s*)+)/(?P<activity_id>\d+)/ordered/$', 'detail', {'type': 'ordered'}),
	(r'^(?P<program_name>(\w+\s*)+)/(?P<activity_id>\d+)/$', 'detail', {'type': 'view'}), #view a particular program's ideas
)
