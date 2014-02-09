from django.shortcuts import render
from django.template import RequestContext
from boards.models import Post

def random(request):
	context = RequestContext(request)
	return render(request, 'index.html', context)
