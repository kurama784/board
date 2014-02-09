from django.shortcuts import render
from django.template import RequestContext
from boards.models import Post
from models import News, TopImage, SecondImage, FooterNews
from datetime import datetime

def index(request):
	context = RequestContext(request)
	return render(request, 'index.html', context)

def main(request):
	time_now = datetime.now()
	db = Post.objects.all()
	context = RequestContext(request)
	context['news'] = News.objects.all()
	context['footer_news'] = FooterNews.objects.all()
	context['time_now'] = time_now
	context['top_image'] = TopImage.objects.all()[:1]
	context['second_image'] = SecondImage.objects.all()[:1]
	context['post_preview'] = db
	return render(request, 'info.html', context)

def menu(request):
	context = RequestContext(request)
        context['posts_per_day'] = float(Post.objects.get_posts_per_day())
	db = Post.objects.all()
        context['db_count'] = db.count()
	return render(request, 'menu.html', context)
