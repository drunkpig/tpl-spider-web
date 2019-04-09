from django.http import Http404
from django.shortcuts import render, redirect, render_to_response
import logging, json
from django.utils.translation import ugettext_lazy as _
from web.forms import TaskForm
from web.models import SpiderTask
from django.contrib import messages
from django.core.cache import cache

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

        task_id, file_id = __save_task(seeds=seeds, client_ip=client_ip, email=email, user_agent='pc', encoding='utf-8',
                                       is_grab_out_link=is_grab_out_link, is_to_single_page=is_to_single_page,
                                       is_full_site=is_full_site, is_ref_model=is_ref_model, to_framework=to_framework)

        messages.success(request, "提交成功")
        resp = redirect("accurate_model")
        resp.set_cookie("fuuid", file_id)
        return resp
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

        task_id, file_id = __save_task(seeds=seeds, client_ip=client_ip, email=email, user_agent='pc', encoding='utf-8',
                                       is_grab_out_link=is_grab_out_link, is_to_single_page=is_to_single_page,
                                       is_full_site=is_full_site, is_ref_model=is_ref_model, to_framework=to_framework)
        messages.success(request, "提交成功")
        resp = redirect("ref_model")
        resp.set_cookie("fuuid", file_id)
        return resp
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

        task_id, file_id = __save_task(seeds=seeds, client_ip=client_ip, email=email, user_agent='pc', encoding='utf-8',
                                       is_grab_out_link=is_grab_out_link, is_to_single_page=is_to_single_page,
                                       is_full_site=is_full_site, is_ref_model=is_ref_model, to_framework=to_framework)

        messages.success(request, "提交成功")
        resp = redirect("fullsite_model")
        resp.set_cookie("fuuid", file_id)
        return resp
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
        task_id, file_id = __save_task(seeds=seeds, client_ip=client_ip, email=email, user_agent='pc', encoding='utf-8',
                                       is_grab_out_link=is_grab_out_link, is_to_single_page=is_to_single_page,
                                       is_full_site=is_full_site, is_ref_model=is_ref_model, to_framework=to_framework)
        messages.success(request, "提交成功")
        resp = redirect("emailpage_model")
        resp.set_cookie("fuuid", file_id)
        return resp
    else:
        return render(request, "emailpage_model.html", {"error": f.errors})


def contact(request):
    return render(request, "contact.html")


def market(request):
    return render(request, "bak/market.html", {'activate_market': 'active'})


def get_web_template(request, template_id):
    return render(request, "get_template.html", {"template_id": template_id})


def status(request):
    max_task_id = __get_taskid_from_cache("max_task_id")
    min_task_id = __get_min_task_id_from_cache()
    cur_file_id = request.COOKIES.get("fuuid")  # file_id
    if cur_file_id is None:
        cur_file_id = 0
    cur_task_id = __get_taskid_from_cache(cur_file_id)
    total_task_cnt = max_task_id - min_task_id
    cur_task_order = cur_task_id - min_task_id

    return render(request, 'status.html',
                  {"total_task": max(0, total_task_cnt), "task_order": max(0, cur_task_order)})


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
    task_id = task.id
    file_id = task.file_id
    cache.set(file_id, task_id)
    cache.set('max_task_id', task_id)  # 每当插入一个，就把这个当成最大的id
    return task_id, file_id


def __get_taskid_from_cache(key):
    val = cache.get(key)
    if val is None:
        val = 0

    return val


def __get_min_task_id_from_cache():
    """
    获取当前处理完成的最新（大）一个task_id
    如果缓存里不存在就从数据库里取，并设置超时时间为1分钟
    select id, file_id,  from spider_task where status='C' order by gmt_modified desc limit 1;
    :return:
    """
    task = SpiderTask.objects.filter(status='C').only("file_id").order_by("-gmt_modified")[0]
    if task:
        min_task_id = task.id
        cache.set("min_task_id", min_task_id, timeout=60)
    else:
        min_task_id = 0
    return min_task_id
