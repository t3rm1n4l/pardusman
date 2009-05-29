# Create your views here.
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import auth

from pardusman.wizard.models import UserProfile
from pardusman.wizard.forms import RegistrationForm
import datetime,random,hashlib
from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import send_mail

from pardusman import settings
import os,re


def home(request):
	site_template  = get_template('template.html')
	html = site_template.render(Context({}))
	return HttpResponse(html)


def ajax_pool(request):

	if request.user:
		user = str(request.user.username)

	
	return render_to_response('content_pool.html',{'user':user, 'repos':repositories(),'package_map':packages()})


def repositories():

	repo_urls = settings.REPOS_URL
	regex = re.compile('<SourceName>(.*)</SourceName>')
	repos = {}

	
	for repo in os.listdir(repo_urls):
		if os.path.exists(os.path.join(repo_urls,repo,"pisi-index.xml")):
			temp = open(os.path.join(repo_urls,repo,"pisi-index.xml"))
			repos[re.findall(regex, temp.read(100))[0]] = os.path.join(repo_urls,repo)
			temp.close()

	return repos	



###############################################################
# TODO: XML Packages parser
# get XML file from selected repository
###############################################################
def packages():
	components = ['system-base','system-multimedia']
	packages = [('package1','system-base'),('package2','system-base'),('package3','system-multimedia')]

	package_map = {}
	
	def map_generate(pkgs):
		if pkgs[1] == comp:
			return pkgs[0]

	for comp in components:
		P = map(map_generate,packages)
		package_map[comp] = [ pkg for pkg in P if pkg is not None] 
		'''Or same can be done filter(None,P)'''

	return package_map



###############################################################
# TODO: Email Confirmation
# Also deal the forms, inside class functions exection problems
###############################################################


def register_user(request):
	
	if request.GET:
		new_data = request.GET.copy()
		form = RegistrationForm(new_data)
	
		valid_user=True
	
	
		for i in new_data.values():
			if i == "":
				return HttpResponse("Do not leave as blank")	

		try:
			User.objects.get(username=str(form.data['user']))
			return HttpResponse("Username already taken !")
		except User.DoesNotExist:
			valid_user=False

		
		if form.is_valid() == False:
			return HttpResponse("Invalid Email ID")


		if valid_user==False and form.data['password1']==form.data['password2']:
			if len(form.data['password1']) < 6:
				return HttpResponse("Passwords should be atleast <br /> 6 characters in length")
			new_user = form.save()
			salt = hashlib.new('sha',str(random.random())).hexdigest()[:5]
			activation_key = hashlib.new('sha',salt+new_user.username).hexdigest()
			key_expires = datetime.datetime.today()+datetime.timedelta(2)
			new_profile = UserProfile(user=new_user,activation_key=activation_key,key_expires=key_expires)
			new_profile.save()

			return HttpResponse('True')
		else:
			return HttpResponse('Re-enter passwords again.')
	else:
		
		return HttpResponse('GET request failed.')


def user_login(request):
	if request.GET:
		new_data = request.GET.copy()
		if new_data.has_key('logout'):
			auth.logout(request)
			return HttpResponse('True')

		user = str(new_data['username'])
		password = str(new_data['password'])
		user_session = auth.authenticate(username=user,password=password)

		if user_session:

			auth.login(request,user_session)
			return HttpResponse('True')
		else:
			return HttpResponse('False')


		return HttpResponse('False')



def is_logged_in(request):
	if request.user.is_authenticated():
		return HttpResponse(str(request.user.username))
	else:
		return HttpResponse('False')


###############################################################
# TODO: Forgot Password
# Dealing forgot password
###############################################################

def forgot_password(request):
	pass
