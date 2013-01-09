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

from brainstorming.models import UserProfile, Group, Program, Brainstorming, TopN, Pairwise, Participant, Node, PairwiseVote
from brainstorming.models import Survey, SurveyGroup, SurveyRespondent, SurveyQuestion, SurveyDataPoint
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib import admin
from django.forms import ModelForm

admin.site.register(UserProfile)
admin.site.register(Program)
admin.site.register(Brainstorming)
admin.site.register(Pairwise)
admin.site.register(TopN)
admin.site.register(Participant)
admin.site.register(PairwiseVote)
admin.site.register(Node)
admin.site.register(Group)

admin.site.register(Survey)
admin.site.register(SurveyGroup)
admin.site.register(SurveyRespondent)
admin.site.register(SurveyQuestion)
admin.site.register(SurveyDataPoint)

class UserForm(ModelForm):
    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        #self.fields['email'].required = True
        #self.fields['first_name'].required = True
        #self.fields['last_name'].required = True

class UserAdmin(admin.ModelAdmin):
	form = UserForm
	#list_display = ('first_name','last_name','email','is_active')
	exclude = ('password',)
	
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

'''
class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True	
	
	class Meta:
		exclude = ['password']
		
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
'''
'''
class UserForm(forms.ModelForm):
    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        #self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

class UserAdmin(admin.ModelAdmin):
    #form = UserForm
	list_display = ('first_name','last_name','is_active')
	exclude = ['password']


class UserAdmin(admin.ModelAdmin):
	exclude = ['password']
	pass

admin.site.unregister(User)
admin.site.register(User)
'''