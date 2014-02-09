from django.contrib import admin
from boards.models import Post, Tag, User, Ban, Thread
from boards.models.banners import RandomBanners

class PostAdmin(admin.ModelAdmin):

    list_display = ('id', 'title', 'slide_thumbnail')
    list_filter = ('pub_time', 'thread_new', 'poster_ip')
    search_fields = ('id', 'title', 'text', 'poster_ip')


class TagAdmin(admin.ModelAdmin):

    list_display = ('name', 'linked')
    list_filter = ('linked',)


class UserAdmin(admin.ModelAdmin):

    list_display = ('user_id', 'rank')
    search_fields = ('user_id',)


class ThreadAdmin(admin.ModelAdmin):

    def title(self, obj):
        return obj.get_opening_post().title

    def reply_count(self, obj):
        return obj.get_reply_count()

    list_display = ('id', 'title', 'reply_count', 'archived')
    list_filter = ('bump_time', 'archived')
    search_fields = ('id', 'title')

admin.site.register(Post, PostAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Ban)
admin.site.register(Thread, ThreadAdmin)
