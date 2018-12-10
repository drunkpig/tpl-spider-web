from django import forms
from django.utils.translation import ugettext_lazy as _


class TaskForm(forms.Form):
    seeds = forms.CharField(
        required=True,
        max_length=1000,
        widget=forms.Textarea
    )
    user_agent = forms.ChoiceField(
        choices=(('pc','PC Browser'),
                 ('ipad', 'Ipad Browser'),
                 ),
        initial='pc',
        widget=forms.Select

    )
    encoding = forms.ChoiceField(
        choices=(
            ('utf-8','utf-8'),
            ('gbk', "gbk"),
            ('gb2312', 'gb2312'),
        ),
        initial='utf-8',
        widget=forms.Select
    )

    is_grab_out_link = forms.BooleanField(
        # choices=(
        #     (True, _('Yes')),
        #     (False, _("No")),
        # ),
        initial=False,
        widget=forms.Select(choices=(
            (True, _('Yes')),
            (False, _("No")),
        ))
    )
