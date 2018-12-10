from django.http import Http404
from django.shortcuts import render
import logging,json

from web.forms import TaskForm
from web.models import SpiderTask

logger = logging.getLogger(__name__)


def index(request):
    if request.method=='GET':
        f = TaskForm()
        return render(request, "index.html", {'form':f})
    elif request.method=='POST':
        f = TaskForm(request.POST)
        if f.is_valid():
            client_ip = __get_client_ip(request)
            SpiderTask.objects.create(**{'seeds':__seeds_url_list_to_json(f.cleaned_data['seeds']),
                                       'user_agent':f.cleaned_data['user_agent'],
                                       'encoding': f.cleaned_data['encoding'],
                                       'is_grab_out_link': f.cleaned_data['is_grab_out_link'],
                                       'ip':client_ip, 'user_id_str':'test_user'}) # TODO
            # TODO return
        else:
            return render(request, "index.html", {"error": f.errors, 'form': f})
    else:
        raise Http404("page not found")


def __get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def __seeds_url_list_to_json(seeds_str):
    url_list = seeds_str.split('\n')
    url_list = list(map(lambda u: u.strip(), url_list))
    return json.dumps(url_list)


