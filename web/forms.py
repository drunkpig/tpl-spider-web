#from captcha.fields import CaptchaField
from captcha.widgets import ReCaptchaV3
from django import forms
from django.utils.translation import ugettext_lazy as _
import validators
import json
from captcha.fields import ReCaptchaField

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

    is_grab_out_link = forms.BooleanField(
        required=False,
    )

    is_ref_model = forms.BooleanField(
        required=False,
    )

    is_full_site = forms.BooleanField(
        required=False,
    )

    is_to_single_page = forms.BooleanField(
        required=False,
    )

    captcha = ReCaptchaField(widget=ReCaptchaV3)

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

    def __is_url_valid(self):
        url_list = self.cleaned_data['seeds']

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

    def __fullsite_model_option_verify(self):
        """
        is_grab_out_link 需要和 is_ref_model 互斥。
        如果不是互斥那么报错。
        :return:
        """
        is_grab_out_link = self.cleaned_data['is_grab_out_link']
        is_ref_model = self.cleaned_data['is_ref_model']

        if is_grab_out_link is None and is_ref_model is None:
            self.add_error("is_grab_out_link", "[抓取引用的资源]和[是否引用外部资源]需要互斥")
            return False
        elif is_grab_out_link == is_ref_model:
            self.add_error("is_grab_out_link", "[抓取引用的资源]和[是否引用外部资源]需要互斥")
            return False

        return True

    def is_valid(self, check_model=None):
        b1 = super().is_valid()
        b2 = self.__is_url_valid()
        b3 = True
        if check_model=='fullsite':
            b3 = self.__fullsite_model_option_verify()
        return b1 and b2 and b3
