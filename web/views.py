from django.http import Http404
from django.shortcuts import render, redirect
import logging,json
from django.utils.translation import ugettext_lazy as _
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
            if __is_user_have_no_task(f.cleaned_data['email']):
                client_ip = __get_client_ip(request)
                task = SpiderTask.objects.create(**{'seeds':__seeds_url_list_to_json(f.cleaned_data['seeds']),
                                           'user_agent':f.cleaned_data['user_agent'],
                                           'encoding': f.cleaned_data['encoding'],
                                           'is_grab_out_link': f.cleaned_data['is_grab_out_link'],
                                           'ip':client_ip,
                                           'user_id_str':f.cleaned_data['email']})
                request.session['task_id']=task.id
                return redirect('index')
            else:
                # 用户已经提交了一个任务
                return render(request, "index.html", {"task_dup_error": _('您已经提交了一个任务，请等待任务完成再提交新的任务'), 'form': f, 'activate_index': 'active'})
        else:
            return render(request, "index.html", {"error": f.errors, 'form': f, 'activate_index':'active'})
    else:
        raise Http404("page not found")


def market(request):
    return render(request, "market.html", {'activate_market':'active'})


# def status(request):
#     total_task = SpiderTask.objects.filter(status__in=['I', 'P']).count()
#     task_id = request.session.get("task_id")
#     if task_id is not None:
#         task_order = SpiderTask.objects.filter(id__lt=task_id, status__in=['I', 'P']).count()
#         return render(request, 'status.html', {"total_task":total_task, "task_order":task_order, 'activate_status':'active'})
#     else:
#         return render(request, 'status.html', {"total_task": total_task, 'activate_status':'active'})


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


def __is_user_have_no_task(email):
    cnt = SpiderTask.objects.filter(status__in=['I', 'P'], user_id_str=email).count()
    return cnt==0
