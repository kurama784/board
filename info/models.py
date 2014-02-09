from django.db import models
from boards import thumbs
from sorl.thumbnail.main import DjangoThumbnail

IMAGE_THUMB_SIZE = (200, 150)

class News(models.Model):
	pub_time = models.DateTimeField()
	title = models.CharField(max_length=20)
	text = models.CharField(max_length=200)
	def __unicode__(self):
		return u'%s %s' % (self.title, self.pub_time)
class FooterNews(models.Model):
	pub_time = models.DateTimeField()
	title = models.CharField(max_length=50)
	text = models.CharField(max_length=200)
	def __unicode__(self):
		return u'%s %s' % (self.title, self.pub_time)

class TopImage(models.Model):
	title = models.CharField(max_length=20)
	address = models.URLField(default = "")
	def top_image_thumbnail(self):
		if self.address:
			thumb = self.address
			return '<img src="%s" />' % thumb
		return None
    	top_image_thumbnail.allow_tags = True
	def __unicode__(self):
		return u'%s' % (self.title)

class SecondImage(models.Model):
	title = models.CharField(max_length=20)
	address = models.URLField(default = "")

	def second_image_thumbnail(self):
		if self.address:
			thumb = self.address
			return '<img src="%s" />' % thumb
		return None
	second_image_thumbnail.allow_tags = True

	def __unicode__(self):
		return u'%s' % (self.title)

class RandomBanners(models.Model):
	title = models.CharField(max_length=20)
	address = models.URLField()

	def random_banners_thumbnail(self):
		if self.address:
			thumb = self.address
			return '<img src="%s" />' % thumb
		return None
	random_banners_thumbnail.allow_tags = True

	def __unicode__(self):
		return u'%s' % (self.title)
