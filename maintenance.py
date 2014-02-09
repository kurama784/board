"""
Maintenance script for neboard imageboard. Use this to update data after
migrations etc.
"""

from boards.models import Post
from boards import views

def update_posts():
    for post in Post.objects.all():
	print 'Updating post #' + str(post.id)

	post.save()

	Post.objects.connect_replies(post)
