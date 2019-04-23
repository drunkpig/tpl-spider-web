"""tpl_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from web import views as web_views
from web.error_views import page_not_found, page_error

urlpatterns = i18n_patterns(
    #path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', web_views.index, name='home'),
    path('index', web_views.index, name='index'),

    path('accurate-template', web_views.accurate_template, name='accurate_template'),
    path('accurate-task', web_views.accurate_task, name='accurate_task'),
    path('fullsite-template', web_views.fullsite_template, name='fullsite_template'),
    path('fullsite-task', web_views.fullsite_task, name='fullsite_task'),
    path('ref-template', web_views.ref_template, name='ref_template'),
    path('ref-task', web_views.ref_task, name='ref_task'),
    path('email-template', web_views.email_template, name='email_template'),
    path('emailtemplate-task', web_views.email_task, name='email_task'),

    path('market', web_views.market, name='market'),
    path('help', web_views.help, name='help'),
    path('contact', web_views.contact, name='contact'),
    path('get-web-template/<str:template_id>', web_views.get_web_template, name='get_template'),
    path('status', web_views.status, name='status'),
    path('test', web_views.test, name="test"),
    prefix_default_language=False,
)

handler404 = page_not_found
handler500 = page_error
