from captcha.fields import CaptchaField
from django import forms
from django.utils.translation import ugettext_lazy as _
import validators
import json


class UrlListField(forms.CharField):
    """

    """
    def to_python(self, value):
        url_list = value.split('\n')
        url_list = list(map(lambda u: u.strip(), url_list))
        return json.dumps(url_list)


class TaskForm(forms.Form):
    seeds = UrlListField(
        required=True,
        max_length=1000
    )

    email = forms.EmailField(
        required=True,
        max_length=50,
        # widget=forms.TextInput(attrs={'id': 'email', 'class': "form-control"})
    )

    to_framework = forms.CharField(
        required=True,
        max_length=50,
        # widget=forms.TextInput(attrs={'id': 'email', 'class': "form-control"})
    )
    #
    # is_grab_out_link = forms.BooleanField(
    #
    #     required=False,
    #     initial=False,
    #     widget=forms.Select(
    #         choices=(
    #             (True, _('Yes')),
    #             (False, _("No")),
    #         ),
    #         attrs={'id': 'is_grab_out_link'}
    #     )
    # )

    # captcha = CaptchaField()

    def __is_url_valid(self, url_list):
        b = True
        lst = json.loads(url_list)
        try:
            for u in lst:
                b = b and validators.url(u)
                if not b:
                    self.add_error("seeds", "URL format error")
                    return b
            return b
        except:
            self.add_error("seeds", "URL format error")
            return False

    def is_valid(self):
        b1 = super().is_valid()
        b2 = self.__is_url_valid(self.cleaned_data['seeds'])
        return b1 and b2
