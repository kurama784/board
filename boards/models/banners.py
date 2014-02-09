from django.db import models

class RandomBanners(models.Model):
	title = models.CharField(max_length=20)
	address = models.URLField()
	def __unicode__(self):
		return u'%s' % (self.title)
