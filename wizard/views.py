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
from xml.etree import ElementTree as ET

def home(request):
	site_template  = get_template('template.html')
	html = site_template.render(Context({}))
	return HttpResponse(html)


def ajax_pool(request):

	if request.user:
		user = str(request.user.username)

	
	return render_to_response('content_pool.html',{'user':user, 'repos':repositories(), 'wallpapers':wallpapers(),'media':media()})


###############################################################
# TODO: Package HTML generator
# Generate .html packages html file for each repo
################################################################


def packages_pool_generator(request):
	template = get_template('packages.html')
	html = template.render(Context({'package_map':packages()}))
	
	handle = file(settings.MEDIA_ROOT + '/templates/repo.html',"w")
	handle.write(html)
	return HttpResponse("Done")



###############################################################
# TODO: Pagination with package widget
# For improving the package widget efficiency
################################################################

def packages_pool(request):
	return render_to_response('repo.html',{})


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



def packages():
	
	components = set()
	packages =[]

	tree = ET.parse(settings.REPOS_URL+'/repo1/'+'pisi-index.xml')
	pkgs = tree.findall('Package')
	for p in pkgs:
		name = p.find('Name').text
		partof = p.find('PartOf').text.replace('.','-')
		packages.append((name,partof))
		components.add(partof)



	package_map = {}
	
	def map_generate(pkgs):
		if pkgs[1] == comp:
			return pkgs[0]

	for comp in components:
		P = map(map_generate,packages)
		package_map[comp] = [ pkg for pkg in P if pkg is not None] 
		'''Or same can be done filter(None,P)'''

	return package_map




def wallpapers():
	
	wallpaper_dir = 'wallpapers'
	prefix_path = os.path.join(settings.MEDIA_URL,'templates')
	return [ os.path.join(wallpaper_dir,x) for x in os.listdir(os.path.join(prefix_path,wallpaper_dir)) ]


def media():

	media = {'iso':'ISO Image','usb-drive':'USB disk','qemu':'QEMU Image','vmware':'VMWare Image','xen':'Xen Image'}

	return media


###############################################################
# TODO: Email Confirmation
# Also deal the forms, inside class functions exection problems
###############################################################


###############################################################
# TODO: OpenID authentication
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
