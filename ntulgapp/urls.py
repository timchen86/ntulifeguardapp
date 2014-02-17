from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'ntulgapp.views.login_view'),
    url(r'^login$', 'ntulgapp.views.login_view'),
    url(r'^signup$', 'ntulgapp.views.signup_view', {"if_training":False}),
    url(r'^signup_new$', 'ntulgapp.views.signup_view',{"if_training":True}),
    url(r'^management$', 'ntulgapp.views.management_view'),
    url(r'^update_data$', 'ntulgapp.views.update_data_view'),
    url(r'^update_password$', 'ntulgapp.views.update_password_view'),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
)
