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

import os, sys

path='/var/www/html/poet-svn/POET-Django/DjangoProjects/'


if path not in sys.path:
	sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

#from django.core.handlers.wsgi import get_wsgi_application
#application = get_wsgi_application()
from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
