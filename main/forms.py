from django import forms
from django.core.validators import EmailValidator
from django_select2.forms import Select2MultipleWidget, Select2Widget
from django.forms import SelectDateWidget, TimeInput

from .models import Mailer, Client, MailingSettings, MailingStatus


class ClientCreateForm(forms.ModelForm):
    email = forms.EmailField(validators=[EmailValidator(message="Введите корректный email адрес")])

    class Meta:
        model = Client
        fields = ['email', 'first_name', 'last_name', 'middle_name', 'comment']


class MailerCreateForm(forms.ModelForm):
    clients = forms.ModelMultipleChoiceField(
        queryset=Client.objects.all(),
        widget=Select2MultipleWidget,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Получите все настройки, которые уже связаны с существующими рассылками
        existing_settings = MailingSettings.objects.filter(mailer__isnull=False)

        # Исключите существующие настройки из выпадающего списка
        self.fields['mailing_settings'].queryset = MailingSettings.objects.exclude(id__in=existing_settings)

    class Meta:
        model = Mailer
        fields = ['email_message', 'mailing_settings']


class MailingSettingsForm(forms.ModelForm):
    class Meta:
        model = MailingSettings
        fields = ['mailing_time', 'mailing_date', 'mailing_period']

    widgets = {
        'mailing_date': SelectDateWidget(),
        'mailing_time': TimeInput(attrs={'type': 'time'}),
        'mailing_period': Select2Widget,
    }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Установите mailing_status по умолчанию
    #     mailing_status, created = MailingStatus.objects.get_or_create(is_created=True)
    #     self.fields['mailing_status'].initial = mailing_status
