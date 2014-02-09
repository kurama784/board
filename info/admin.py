from django.contrib import admin
from models import News, FooterNews, TopImage, SecondImage, RandomBanners


class TopImageAdmin(admin.ModelAdmin):

    list_display = ('id', 'title', 'top_image_thumbnail')

class SecondImageAdmin(admin.ModelAdmin):

    list_display = ('id', 'title', 'second_image_thumbnail')

class RandomBannersAdmin(admin.ModelAdmin):

    list_display = ('id', 'title', 'random_banners_thumbnail')


admin.site.register(News)
admin.site.register(FooterNews)
admin.site.register(TopImage, TopImageAdmin)
admin.site.register(SecondImage, SecondImageAdmin)
admin.site.register(RandomBanners, RandomBannersAdmin)
