from django.conf.urls import patterns, include, url
from bookmarks.feeds import *
from django.views.generic.simple import direct_to_template
import os.path
from bookmarks.views import *
from django.contrib import admin

admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

site_media = os.path.join(
		os.path.dirname(__file__), 'site_media'
		)

feeds = {
	'recent':RecentBookmarks
}

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Bookmarks.views.home', name='home'),
    # url(r'^Bookmarks/', include('Bookmarks.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
	(r'^$', main_page),
	(r'^user/(\w+)/$', user_page),
	(r'^login/$', 'django.contrib.auth.views.login'),
	(r'logout/$', logout_page),
	(r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
	 {'document_root':site_media}),
	(r'^register/$', register_page),
	(r'^register/success/$', direct_to_template, {
	 'template':'registration/register_success.html'}),
	(r'^modification/$', user_modification_page),
	(r'^save/$', bookmark_save_page),
	(r'^tag/([^\s]+)/$', tag_page),
	(r'^tag/$', tag_cloud_page),
	(r'^search/$', search_page),
	(r'^ajax/tag/autocomplete/$', ajax_tag_autocomplete),
	(r'^vote/$', bookmark_vote_page),
	(r'^popular/$', popular_page),
	(r'^comments/', include('django.contrib.comments.urls')),
	(r'^bookmark/(\d)/$', bookmark_page),
	(r'^nimda/', include(admin.site.urls)),
	(r'^feeds/(?P<url>.*)/$',
	 'django.contrib.syndication.views.Feed',
	 {'feed_dict':feeds})
)
