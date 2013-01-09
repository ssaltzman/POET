"""
13. Adding hooks before/after saving and deleting

To execute arbitrary code around ``save()`` and ``delete()``, just subclass
the methods.
"""

from django.db import models


class Person(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)

    def __init__(self, *args, **kwargs):
        super(Person, self).__init__(*args, **kwargs)
        self.data = []

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        self.data.append("Before save")
         # Call the "real" save() method
        super(Person, self).save(*args, **kwargs)
        self.data.append("After save")

    def delete(self):
        self.data.append("Before deletion")
        # Call the "real" delete() method
        super(Person, self).delete()
        self.data.append("After deletion")
