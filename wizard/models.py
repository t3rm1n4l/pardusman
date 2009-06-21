from django.db import models
from pardusman.wizard.fields import DictionaryField


# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.OneToOneField(User)
	activation_key = models.CharField(max_length=40)
	key_expires = models.DateTimeField()

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


