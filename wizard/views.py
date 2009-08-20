# -*- coding: utf-8 -*-
# Create your views here.
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import auth

from pardusman.wizard.models import UserProfile
from pardusman.wizard.forms import *
import datetime,random,hashlib
from django.shortcuts import render_to_response, get_object_or_404
from django.core.mail import send_mail
from django.core.cache import cache

from pardusman import settings
import os,re,tempfile, time

from xml.etree import ElementTree as ET


#Home page
def home(request):
	site_template  = get_template('template.html')
	html = site_template.render(Context({}))
	return HttpResponse(html)


#Process upload requests for home_file, wallpaper and release file
def upload(request):

	if request.FILES.has_key('home_file'):
		if request.FILES['home_file'].content_type.endswith('zip') or request.FILES['home_file'].content_type.endswith('tar.gz') or request.FILES['home_file'].content_type.endswith('bz2'):
			tmp = tempfile.mkstemp(suffix='.%s' % request.FILES['home_file'].name.split('.',1)[1],prefix='home_',dir=settings.TMP_FILES)[1]
			fd = file(tmp,'w')
			for chunk in request.FILES['home_file'].chunks():
				fd.write(chunk)
			fd.close()
			request.session['home_file'] = os.path.basename(tmp)
			return HttpResponse("{ error:'error', \n msg:'success' \n}")

	if request.FILES.has_key('wallpaper_file'):
		if request.FILES['wallpaper_file'].content_type.startswith('image'):
			tmp = tempfile.mkstemp(suffix='.%s' % request.FILES['wallpaper_file'].name.split('.',1)[1],prefix='wallpaper_',dir=os.path.join(settings.TMP_WALLPAPERS,'user_wallpapers'))[1]
			fd = file(tmp,'w')
			for chunk in request.FILES['wallpaper_file'].chunks():
				fd.write(chunk)
			fd.close()
			png_file = tmp.split(".")[0] + ".png"
			os.system("/usr/bin/convert %s %s" %(tmp,png_file))

			fd = os.system("/usr/bin/convert %s  -resize 'x90' %s" % (tmp, os.path.join(settings.MEDIA_URL,'templates/user_wallpapers/',os.path.basename(png_file))))

			return HttpResponse("{ error:'error', \n msg:'%s' \n}" % os.path.join('user_wallpapers',os.path.basename(png_file)))


	if request.FILES.has_key('release_file'):
		if request.FILES['release_file'].content_type.startswith('text'):
			tmp = tempfile.mkstemp(suffix='.%s' % request.FILES['release_file'].name.split('.',1)[1] ,prefix='release_',dir=settings.TMP_FILES)[1]
			fd = file(tmp,'w')
			for chunk in request.FILES['release_file'].chunks():
				fd.write(chunk)
			fd.close()
			request.session['release_file'] = os.path.basename(tmp)

			return HttpResponse("{ error:'error', \n msg:'success' \n}")
	
	del request.session['home_file'] 
	del request.session['release_file'] 


	return HttpResponse('False')
    

def ajax_pool(request):

	if request.user:
		user = str(request.user.username)

	
	return render_to_response('content_pool.html',{'user':user, 'repos':repositories(), 'wallpapers':wallpapers(),'media':media()})



#Process each page load request 
def page_loader(request):
	post = request.POST.copy()
	
	for p,k in post.items():
		if p not in ['username','password','password1','password2']:
			request.session[p] = k
	if post.has_key('username'):
		request.session['user'] = post['username']

	if post['page'] == 'page1':
		user = request.user.username
		returns = render_to_response('page1.html',{'user':user})

	elif post['page'] == 'page2':
		repo = repositories()
		returns = render_to_response('page2.html',{'repos':repo}) 	

	elif post['page'] == 'page3':

		returns = render_to_response('page3.html',{'languages':languages()})

	elif post['page'] == 'page4':
		request.session['languages'] = request.POST.getlist('language')
		returns = render_to_response('page4.html',{})
		
	elif post['page'] == 'page5':

		
		returns = render_to_response('%s.html' % request.session['repo_type'],{})

	elif post['page'] == 'page6':
		wall = wallpapers()
		if post.has_key('wallpaper'):
			wall.append(post['wallpaper'])

		returns = render_to_response('page6.html',{'wallpapers':wall})

	elif post['page'] == 'page7':
		returns = render_to_response('page7.html',{'media':media()})

	elif post['page'] == 'userlog':
		from pardusman.wizard.models import Userlogs
		
		ulog = Userlogs.objects.get_or_create(username=request.user.username)
		if ulog[1] == False:
			listings = ulog[0].scheduled_tasks.order_by('date')
		else:
			listings = []
		
		returns = render_to_response('page_userlog.html',{'userlogs':listings})

	elif post['page'] == 'page8':
		alls=""
		p ={}
		for k,v in request.session.items():
			alls=alls+str(k)+' : '+str(v)+'\n'	
			p[k] = v
		file('/tmp/tp','w').write(alls)


		generate_project_file(p,request.user.username)


		for key in request.session.keys():
			if not key.startswith('_'):
				del request.session[key]



		returns = render_to_response('page8.html',{})
	else:	
                returns = render_to_response('page0.html',{})
	

	return returns

#Generate tar.gz project file from the configuration collected from web wizard
def generate_project_file(pool,username):
	from pardusman.repotools.project import Project
	from django.core.cache import cache
	from pardusman.wizard.models import Userlogs,scheduled_distro,buildfarm_queue
	import tarfile,shutil

	xml_file = tempfile.mkstemp(suffix='.xml', prefix='project_',dir=os.path.join(settings.TMP_FILES))[1]
	project_file = tempfile.mkstemp(suffix='.tar.gz', prefix='project_',dir=os.path.join(settings.PROJECT_FILES))[1]

	tar = tarfile.open(project_file,'w:gz')



	project = Project()
	project.title = pool['image_title']
	project.repo = pool['repo_type']
	project.media = pool['image_type']

	project.type = pool['image_mode']

	if pool.has_key('hostname'):
		project.hostname = pool['hostname']

	if pool.has_key('default_user'):
		project.username = pool['default_user']

	if pool.has_key('default_password1'):
		project.password = pool['default_password1']

	if pool.has_key('wallpaper'):
		if pool['wallpaper'] !='null':
			project.wallpaper = pool['wallpaper']
			tar.add(os.path.join(settings.TMP_WALLPAPERS,project.wallpaper),project.wallpaper)

	

	if pool.has_key('release_file'):
		project.release_files = 'RELEASE.txt'
		tar.add(os.path.join(settings.TMP_FILES,pool['release_file']),'RELEASE.txt')

	if pool.has_key('home_file'):
		project.user_contents = 'user_contents.tar.gz' 
		tar.add(os.path.join(settings.TMP_FILES,pool['home_file']),'user_contents.tar.gz')

	lp = cache.get('live_packages')
	lp.fix_components()
	
	project.selected_packages = list(lp.packages)
	project.all_packages = list(lp.required_packages)
	project.selected_components = list(lp.components)
	project.default_language = pool['languages'][0]
	project.selected_languages = pool['languages']
	project.save(xml_file)

	tar.add(xml_file,'project.xml')

	tar.close()

	os.chmod(project_file,655)

	#Get the user object if exists else create new object
	ulog,flag = Userlogs.objects.get_or_create(username=username)
	

	if flag == True:
		ulog.username = username

	ulog = Userlogs.objects.get(username=username)
	sched_task = scheduled_distro()
	sched_task.date = time.strftime("%Y-%m-%d")
	sched_task.image_title = project.title
	sched_task.image_url = ''
	sched_task.project_url = os.path.join(settings.BASE_PROJECTS_URL,'projects',os.path.basename(project_file))
	sched_task.image_type = project.type
	sched_task.progress = "Scheduled"
	sched_task.save()
	ulog.scheduled_tasks.add(sched_task)
	ulog.save()
	
	
	#Add project to the buildfarm queue
	queue = buildfarm_queue()
	queue.id = sched_task.id 
	queue.date = sched_task.date
	queue.project_file = project_file
	queue.save()
	



###############################################################
# TODO: Package HTML generator
# Generate .html packages html file for each repo
################################################################
def packages_pool_generator(request):
	template = get_template('packages.html')
	for repo in repositories():
		html = template.render(Context({'package_map':packages(os.path.join(settings.REPOS_URL,repo))}))
		handle = file(os.path.join(settings.MEDIA_ROOT, 'templates/pages/','%s.html' %repo),"w")
		handle.write(html)
	return HttpResponse("Done")



###############################################################
# TODO: Pagination with package widget
# For improving the package widget efficiency
################################################################

def packages_pool(request):
	return render_to_response('repo.html',{})

#Collect the names of repositories
def repositories():
	repo_urls = settings.REPOS_URL
	repos = set()
	
	for repo in os.listdir(repo_urls):
		if os.path.exists(os.path.join(repo_urls,repo,"pisi-index.xml")):
			repos.add(repo)
	return repos	


#Parse packages from xml config
def packages(URL):
	
	components = set()
	packages =[]

	tree = ET.parse(os.path.join(URL,'pisi-index.xml'))
	pkgs = tree.findall('Package')
	for p in pkgs:
		name = p.find('Name').text
		partof = p.find('PartOf').text.replace('.','-')
		packages.append((name,partof))
		components.add(partof)

	from django.utils.datastructures import SortedDict

	package_map = SortedDict()
	
	def map_generate(pkgs):
		if pkgs[1] == comp:
			return pkgs[0]

	components = list(components)
	components.sort()

	for comp in components:
		P = map(map_generate,packages)
		package_map[comp] = [ pkg for pkg in P if pkg is not None] 
		'''Or same can be done filter(None,P)'''

	return package_map


#Supported Languages
def languages():
	lang =  {
    "ca_ES": "Catalan",
    "de_DE": "Deutsch",
    "es_ES": "Spanish",
    "fr_FR": "French",
    "it_IT": "Italian",
    "nl_NL": "Dutch",
    "pl_PL": "Polish",
    "pt_BR": "Brazilian Portuguese",
    "sv_SE": "Svenska",
    "tr_TR": "Turkish",
}

	return lang

#Return with wallpaper list
def wallpapers():
	
	wallpaper_dir = 'wallpapers'
	prefix_path = os.path.join(settings.MEDIA_URL,'templates')
	return [ os.path.join(wallpaper_dir,x) for x in os.listdir(os.path.join(prefix_path,wallpaper_dir)) ]


#Update the packages list in LivePackagePool memcached object and calculate the size
def update_size(request):
	items = []
	for item in request.POST:
		if item.endswith('_component') or item.endswith('_package'):
			items.append(item)



	if not cache.has_key('repo'):
		from pardusman.repotools.packages import Repository, LivePackagePool
		repo = Repository(request.session['repo_type'])
		repo.parse_data(os.path.join(settings.REPOS_URL,repo.name,'pisi-index.xml'))
		cache.set('repo',repo)


	from pardusman.repotools.packages import LivePackagePool
	live_packages = LivePackagePool()
	for item in items:
		live_packages.add_item(item)
	size = live_packages.get_size()/(1024.0*1024)
	cache.set('live_packages',live_packages)
	return HttpResponse('<b>Total size: %.2f MB</b>' % size)
  

#Supported media types
def media():
	#Disabled all except ISO temporarily.
	#media = {'iso':'ISO Image','usb-drive':'USB disk','qemu':'QEMU Image','vmware':'VMWare Image','xen':'Xen Image'}
	media = {'iso':'ISO Image'}

	return media



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
			new_profile = UserProfile(user=new_user,activation_key=activation_key,key_expires=key_expires,is_active=True)
			new_profile.save()

			return HttpResponse('True')
		else:
			return HttpResponse('Re-enter passwords again.')
	else:
		
		return HttpResponse('GET request failed.')



#User login
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


#To check user logged in or not
def is_logged_in(request):
	if request.user.is_authenticated():
		return HttpResponse(str(request.user.username))
	else:
		return HttpResponse('False')


#Confirm user registration up on e-mail link
def user_confirm(request, name, key):

	u = User.objects.get(username=name)
	if u.is_active:
		return render_response(request, 'user/confirm.html', {'actived': True})
	elif u.get_profile().activation_key == key:
		if u.get_profile().key_expires < datetime.datetime.today():
			u.delete()
			return render_response(request, 'user/confirm.html', {'key_expired': True})
		else:
			u.is_active = True
			u.save()
			return render_response(request, 'user/confirm.html', {'ok': True})



def lost_password(request):
	if request.method == 'POST':
		form = LostPasswordForm(request.POST)
		if form.is_valid():
			# generate new key and e-mail it to user
			salt = sha.new(str(random.random())).hexdigest()[8:]
			key = sha.new(salt).hexdigest()

			u = User.objects.get(username=form.cleaned_data['username'])
			lostpwd = LostPassword(user=u)
			lostpwd.key = key
			lostpwd.key_expires = datetime.datetime.today() + datetime.timedelta(1)
			lostpwd.save()

			# mail it
			email_dict = {
                    "SITE_NAME": 'Pardusman',
                    'date': datetime.datetime.now(),
                    'ip': request.META['REMOTE_ADDR'],
                    'user': form.cleaned_data['username'],
                    'link': 'http://pardusman.pardus.org.tr/%s' % key,
                    }

			email_subject = _("%(SITE_NAME)s User Password") % SITE_NAME
			email_body = loader.get_template("mails/password.html").render(Context(email_dict))
			email_to = form.cleaned_data['email']

			send_mail(email_subject, email_body, DEFAULT_FROM_EMAIL, [email_to], fail_silently=True)
			return render_response(request, 'user/lostpassword_done.html')
		else:
			return render_response(request, 'user/lostpassword.html', {'form': form})
	else:
		form = LostPasswordForm()
		return render_response(request, 'user/lostpassword.html', {'form': form})


def change_password(request):
	u = request.user
	password_changed = False

	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		form.user = u

	if form.is_valid() and len(form.cleaned_data['password']) > 0:
		u.set_password(form.cleaned_data['password'])
		u.save()
		password_changed = True
	else:
		form = ChangePasswordForm()


	return render_response(request, 'user/password.html', {
        "form": form,
        "password_changed": password_changed,
        })

def reset_password(request, key):
	if LostPassword.objects.count() == 0:
		return render_response(request, 'user/change_password.html', {'error': True, 'invalid': True})

	lostpwd = LostPassword.objects.get(key=key)
	if lostpwd.is_expired():
		lostpwd.delete()
		return render_response(request, 'user/change_password.html', {'error': True, 'expired': True})
	else:
		if request.method == 'POST':
			form = ResetPasswordForm(request.POST)
			if form.is_valid():
				u = User.objects.get(username=lostpwd.user.username)
				u.set_password(form.cleaned_data['password'])
				u.save()
				lostpwd.delete()
				return render_response(request, 'user/change_password_done.html', {'login_url': LOGIN_URL})
			else:
				return render_response(request, 'user/change_password.html', {'form': form})
		else:
			form = ResetPasswordForm()
			return render_response(request, 'user/change_password.html', {'form': form})
