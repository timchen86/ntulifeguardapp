from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'ntulifeguardapp.views.login_view'),
    url(r'^login$', 'ntulifeguardapp.views.login_view'),
    url(r'^signup$', 'ntulifeguardapp.views.signup_view', {"if_training":False}),
    url(r'^signup_new$', 'ntulifeguardapp.views.signup_view',{"if_training":True}),
    url(r'^management$', 'ntulifeguardapp.views.management_view'),
    url(r'^update_data$', 'ntulifeguardapp.views.update_data_view'),
    url(r'^update_password$', 'ntulifeguardapp.views.update_password_view'),


    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
