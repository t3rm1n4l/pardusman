# -*- coding: utf-8 -*-
# Create your models here.

from django.db import models


from django.db import models
from django.contrib.auth.models import User

#For user information storage
class UserProfile(models.Model):
	user = models.OneToOneField(User)
	is_active = models.BooleanField()
	activation_key = models.CharField(max_length=40)
	key_expires = models.DateTimeField()


'''
#Depricated database implementation. XML and memcached is used instead.
class Dependency(models.Model):
	name = models.CharField(max_length=60,primary_key=True)
	
class Package(models.Model):
	name = models.CharField(max_length=60,primary_key=True)
	size = models.IntegerField(max_length=60)
	part_of = models.CharField(max_length=60)
	dependencies = models.ManyToManyField(Dependency)

class Components(models.Model):
	name = models.CharField(max_length=60,primary_key=True)
	packages = models.ManyToManyField(Dependency)


class Repository(models.Model):
	name = models.CharField(max_length=60,primary_key=True)
	size = models.IntegerField(max_length=60)
	inst_size = models.IntegerField(max_length=60)
	packages = models.ManyToManyField(Package)
	components = models.ManyToManyField(Components)
'''

#Project listings with details
class scheduled_distro(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    log_url = models.URLField()
    image_title = models.CharField(max_length=60)
    image_url = models.URLField()
    image_type = models.CharField(max_length=60)
    project_url = models.URLField()
    progress = models.CharField(max_length=60)

#Attaching user with list of projects by him
class Userlogs(models.Model):
    username = models.CharField(max_length=60,primary_key=True)
    scheduled_tasks = models.ManyToManyField(scheduled_distro)


#For storing list of projects requested for build by user
class buildfarm_queue(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    project_file = models.URLField()

#For storing the list of projects processed currently
class onprogress_queue(models.Model):
    id = models.IntegerField(primary_key=True)
    work_dir = models.URLField()
    image_file = models.URLField()
    status = models.CharField(max_length=60)

