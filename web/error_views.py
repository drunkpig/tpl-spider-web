from django.shortcuts import render


def page_not_found(request):
    return render(request, '404.html')


def page_error(request): # 500
    return render(request, '404.html')


def permission_denied(request):
    return render(request, '404.html')
