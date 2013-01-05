# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed
from bookmarks.models import *

class RecentBookmarks(Feed):
	title=u'장고북마크 | 최신 북마크다'
	link='/feeds/recent/'
	description=u'장고 북마크 서비스를 통해서 등록된 북마크'

	def items(self):
		return Bookmark.objects.order_by('-id')[:10]
