from django.shortcuts import render
from django.template import RequestContext
from boards.models import Thread, Post
def index(request):
	context = RequestContext(request)
	return render(request, 'menu.html', context)
