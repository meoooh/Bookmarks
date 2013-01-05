from django.contrib import admin
from bookmarks.models import *

class AdminBookmark(admin.ModelAdmin):
	list_display = ("title", "link",)
	list_filter = ("user", "tag",)
	ordering = ("title",)
	search_fields = ("title",)

admin.site.register(Bookmark, AdminBookmark,)
admin.site.register(Link,)
admin.site.register(Tag,)
admin.site.register(SharedBookmark,)
