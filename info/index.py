from django.shortcuts import render
from django.template import RequestContext
def index(request):
	context = RequestContext(request)
	return render(request, 'index.html', context)
