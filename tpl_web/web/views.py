from django.shortcuts import render
import logging


logger = logging.getLogger(__name__)


def index(request):
    return render(request, "index.html")


def submit_task(request):
    pass


