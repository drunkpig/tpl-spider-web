from django import forms
from django.utils.translation import ugettext_lazy as _


class TaskForm(forms.Form):
    url_list = forms.CharField(required=True, max_length=1000)
    user_agent = forms.CharField(required=True, max_length=200)
    encoding = forms.CharField(required=True, max_length=10)
