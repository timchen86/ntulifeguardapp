from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'ntulgapp.views.login_view'),
    url(r'^login$', 'ntulgapp.views.login_view'),
    url(r'^signup$', 'ntulgapp.views.signup_view'),
    # url(r'^ntulgapp/', include('ntulgapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
