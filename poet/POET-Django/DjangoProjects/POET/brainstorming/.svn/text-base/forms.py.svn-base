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

from django import forms
from django.contrib import auth
import re

class ValidatingPasswordChangeForm(auth.forms.PasswordChangeForm):
    MIN_LENGTH = 8

    def clean_new_password1(self):
		password1 = self.cleaned_data.get('new_password1')

		# At least MIN_LENGTH long
		if len(password1) < self.MIN_LENGTH:
			raise forms.ValidationError("The new password must be at least %d characters long." % self.MIN_LENGTH)

		test = re.compile(r'/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%*=+:,.?]).+$/')
        # At least one letter and one non-letter
		if not test.match(password1):
			raise forms.ValidationError("The new password must contain at least one lower-case character, one upper-case character, one number and one special character.")
		# ... any other validation you want ...
		return password1