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
from django.contrib import admin
from django.urls import path, include
from web import views as web_views
from web.error_views import page_not_found, page_error

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('', web_views.index, name='home'),
    path('index', web_views.index, name='index'),
    path('market', web_views.market, name='market'),
    path('help', web_views.help, name='help'),
    # path('status', web_views.status, name='status'),
    url(r'^captcha/', include('captcha.urls')),
]

handler404 = page_not_found
handler500 = page_error