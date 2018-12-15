from django import forms
from django.utils.translation import ugettext_lazy as _


class TaskForm(forms.Form):
    seeds = forms.CharField(
        required=True,
        max_length=1000,
        widget=forms.Textarea(attrs={'id': 'seeds', 'class':"form-control", 'rows':'3'})
    )
    user_agent = forms.ChoiceField(
        choices=(('pc','PC Browser'),
                 ('ipad', 'Ipad Browser'),
                 ),
        initial='pc',
        widget=forms.Select(attrs={'id': 'user_agent', 'class':"form-control"})

    )
    encoding = forms.ChoiceField(
        choices=(
            ('utf-8','utf-8'),
            ('gbk', "gbk"),
            ('gb2312', 'gb2312'),
        ),
        initial='utf-8',
        widget=forms.Select(attrs={'id': 'encoding', 'class':"form-control"})
    )

    is_grab_out_link = forms.BooleanField(
        # choices=(
        #     (True, _('Yes')),
        #     (False, _("No")),
        # ),
        required=False,
        initial=False,
        widget=forms.Select(
            choices=(
                (True, _('Yes')),
                (False, _("No")),
            ),
            attrs={'id': 'is_grab_out_link', 'class': "form-control"}
        )
    )

    email = forms.EmailField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'id': 'email', 'class': "form-control"})
    )
