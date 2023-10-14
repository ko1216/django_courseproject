from django import forms
from django_select2.forms import Select2MultipleWidget, Select2Widget
from django.forms import SelectDateWidget, TimeInput

from .models import Mailer, Client, MailingSettings, MailingStatus


class MailerCreateForm(forms.ModelForm):
    clients = forms.ModelMultipleChoiceField(
        queryset=Client.objects.all(),
        widget=Select2MultipleWidget,
    )

    class Meta:
        model = Mailer
        fields = ['email_message', 'mailing_settings']


class MailingSettingsForm(forms.ModelForm):
    class Meta:
        model = MailingSettings
        fields = ['mailing_time', 'mailing_date', 'mailing_period', 'mailing_status']

    widgets = {
        'mailing_date': SelectDateWidget(),
        'mailing_time': TimeInput(attrs={'type': 'time'}),
        'mailing_period': Select2Widget,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Установите mailing_status по умолчанию
        mailing_status, created = MailingStatus.objects.get_or_create(is_created=True)
        self.fields['mailing_status'].initial = mailing_status
