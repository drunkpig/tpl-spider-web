from django.http import Http404
from django.shortcuts import render, redirect
import logging,json

from web.forms import TaskForm
from web.models import SpiderTask

logger = logging.getLogger(__name__)


def index(request):
    if request.method=='GET':
        f = TaskForm()
        return render(request, "index.html", {'form':f, 'activate_index':'active'})
    elif request.method=='POST':
        f = TaskForm(request.POST)
        if f.is_valid():
            client_ip = __get_client_ip(request)
            task = SpiderTask.objects.create(**{'seeds':__seeds_url_list_to_json(f.cleaned_data['seeds']),
                                       'user_agent':f.cleaned_data['user_agent'],
                                       'encoding': f.cleaned_data['encoding'],
                                       'is_grab_out_link': f.cleaned_data['is_grab_out_link'],
                                       'ip':client_ip,
                                       'user_id_str':f.cleaned_data['email']})
            request.session['task_id']=task.id
            return redirect('status')
        else:
            return render(request, "index.html", {"error": f.errors, 'form': f, 'activate_index':'active'})
    else:
        raise Http404("page not found")


def market(request):
    return render(request, "market.html", {'activate_market':'active'})


def status(request):
    total_task = SpiderTask.objects.filter(status__in=['I', 'P']).count()
    task_id = request.session.get("task_id")
    if task_id is not None:
        task_order = SpiderTask.objects.filter(id__lt=task_id, status__in=['I', 'P']).count()
        return render(request, 'status.html', {"total_task":total_task, "task_order":task_order})
    else:
        return render(request, 'status.html', {"total_task": total_task})


def help(request):
    return render(request, "help.html", {'activate_help':'active'})


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
