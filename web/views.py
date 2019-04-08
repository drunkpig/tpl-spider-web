from django.http import Http404
from django.shortcuts import render, redirect
import logging, json
from django.utils.translation import ugettext_lazy as _
from web.forms import TaskForm
from web.models import SpiderTask
from django.contrib import messages

logger = logging.getLogger(__name__)


def index(request):
    return render(request, "index.html")


def accurate_model(request):
    return render(request, "accurate_model.html")


def accurate_task(request):
    f = TaskForm(request.POST)
    if f.is_valid():
        client_ip = __get_client_ip(request)
        seeds = f.cleaned_data['seeds']
        email = f.cleaned_data['email']
        to_framework = f.cleaned_data['to_framework']

        is_grab_out_link = True
        is_ref_model = False
        is_full_site = False
        is_to_single_page = False

        task_id = __save_task(seeds=seeds, client_ip=client_ip, email=email, user_agent='pc', encoding='utf-8',
                              is_grab_out_link=is_grab_out_link, is_to_single_page=is_to_single_page,
                              is_full_site=is_full_site, is_ref_model=is_ref_model, to_framework=to_framework)
        messages.success(request, "提交成功")
        return redirect("accurate_model")
    else:

        return render(request, "accurate_model.html", {"error": f.errors})


def ref_model(request):
    return render(request, "ref_model.html")


def ref_task(request):
    f = TaskForm(request.POST)
    if f.is_valid():
        client_ip = __get_client_ip(request)
        seeds = f.cleaned_data['seeds']
        email = f.cleaned_data['email']
        to_framework = f.cleaned_data['to_framework']

        is_grab_out_link = False
        is_ref_model = True
        is_full_site = f.cleaned_data['is_full_site']
        is_to_single_page = False

        task_id = __save_task(seeds=seeds, client_ip=client_ip, email=email, user_agent='pc', encoding='utf-8',
                              is_grab_out_link=is_grab_out_link, is_to_single_page=is_to_single_page,
                              is_full_site=is_full_site, is_ref_model=is_ref_model, to_framework=to_framework)
        messages.success(request, "提交成功")
        return redirect("ref_model")
    else:
        return render(request, "ref_model.html", {"error": f.errors})


def fullsite_model(request):
    return render(request, "fullsite_model.html")


def fullsite_task(request):
    f = TaskForm(request.POST)
    if f.is_valid('fullsite'):
        client_ip = __get_client_ip(request)
        seeds = f.cleaned_data['seeds']
        email = f.cleaned_data['email']
        to_framework = f.cleaned_data['to_framework']

        is_grab_out_link = f.cleaned_data['is_grab_out_link']
        is_ref_model = f.cleaned_data['is_ref_model']
        is_full_site = True
        is_to_single_page = False

        task_id = __save_task(seeds=seeds, client_ip=client_ip, email=email, user_agent='pc', encoding='utf-8',
                              is_grab_out_link=is_grab_out_link, is_to_single_page=is_to_single_page,
                              is_full_site=is_full_site, is_ref_model=is_ref_model, to_framework=to_framework)
        messages.success(request, "提交成功")
        return redirect("fullsite_model")
    else:
        return render(request, "fullsite_model.html", {"error": f.errors})


def emailpage_model(request):
    return render(request, "emailpage_model.html")


def emailpage_task(request):
    f = TaskForm(request.POST)
    if f.is_valid():
        client_ip = __get_client_ip(request)
        seeds = f.cleaned_data['seeds']
        email = f.cleaned_data['email']
        to_framework = f.cleaned_data['to_framework']

        is_grab_out_link = True
        is_ref_model = False
        is_full_site = False
        is_to_single_page = True
        task_id = __save_task(seeds=seeds, client_ip=client_ip, email=email, user_agent='pc', encoding='utf-8',
                              is_grab_out_link=is_grab_out_link, is_to_single_page=is_to_single_page,
                              is_full_site=is_full_site, is_ref_model=is_ref_model, to_framework=to_framework)
        messages.success(request, "提交成功")
        return redirect("emailpage_model")
    else:
        return render(request, "emailpage_model.html", {"error": f.errors})


def contact(request):
    return render(request, "contact.html")


def market(request):
    return render(request, "bak/market.html", {'activate_market': 'active'})


def get_web_template(request, template_id):
    return render(request, "get_template.html", {"template_id": template_id})


# def status(request):
#     total_task = SpiderTask.objects.filter(status__in=['I', 'P']).count()
#     task_id = request.session.get("task_id")
#     if task_id is not None:
#         task_order = SpiderTask.objects.filter(id__lt=task_id, status__in=['I', 'P']).count()
#         return render(request, 'status.html', {"total_task":total_task, "task_order":task_order, 'activate_status':'active'})
#     else:
#         return render(request, 'status.html', {"total_task": total_task, 'activate_status':'active'})


def help(request):
    return render(request, "help.html", {'activate_help': 'active'})


def __get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def __is_user_have_no_task(email):
    cnt = SpiderTask.objects.filter(status__in=['I', 'P'], user_id_str=email).count()
    return cnt == 0


def __save_task(seeds, client_ip, email, user_agent, encoding, is_grab_out_link, is_to_single_page, is_full_site,
                is_ref_model, to_framework):
    """

    :param client_ip:
    :param seeds:
    :param email:
    :param user_agent:
    :param encoding:
    :param is_grab_out_link:
    :param is_to_single_page:
    :param is_full_site:
    :param is_ref_model:
    :param to_framework:
    :return:
    """
    task = SpiderTask.objects.create(
        seeds=seeds,
        ip=client_ip,
        email=email,
        user_agent=user_agent,
        encoding=encoding,
        is_grab_out_link=is_grab_out_link,
        is_to_single_page=is_to_single_page,
        is_full_site=is_full_site,
        is_ref_model=is_ref_model,
        to_framework=to_framework
    )
    return task.id
