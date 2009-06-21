from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^pardusman/', include('pardusman.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
    (r'^pardusman/$','pardusman.wizard.views.home'),
    (r'^pardusman/log_in$','pardusman.wizard.views.user_login'),
    (r'^pardusman/update_size$','pardusman.wizard.views.update_size'),
    (r'^pardusman/upload$','pardusman.wizard.views.upload'),
    (r'^pardusman/packages_pool_generator$','pardusman.wizard.views.packages_pool_generator'),
    (r'^pardusman/ajax_pool$','pardusman.wizard.views.ajax_pool'),
    (r'^pardusman/page_loader$','pardusman.wizard.views.page_loader'),
    (r'^pardusman/packages_pool$','pardusman.wizard.views.packages_pool'),
    (r'^pardusman/register$','pardusman.wizard.views.register_user'),
    (r'^pardusman/is_logged_in$','pardusman.wizard.views.is_logged_in'),
    (r'^pardusman/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': '/home/mycode/pardusman/templates', 'show_indexes': True}),

)
