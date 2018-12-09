from django.http import Http404
from django.shortcuts import render
import logging

from web.forms import TaskForm
from web.models import SpiderTask

logger = logging.getLogger(__name__)


def index(request):
    if request.method=='GET':
        return render(request, "index.html")
    elif request.method=='POST':
        f = TaskForm(request.POST)
        if f.is_valid():
            SpiderTask.objects.create(SpiderTask(*f.cleaned_data))
        else:
            return render(request, "index.html", {"error": f.errors})
    else:
        raise Http404("page not found")

