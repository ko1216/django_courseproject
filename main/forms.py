from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django_select2.forms import Select2MultipleWidget, Select2Widget
from django.forms import SelectDateWidget, TimeInput

from .models import Mailer, Client, MailingSettings, MailingPeriod, EmailMessage


class ClientCreateForm(forms.ModelForm):
    email = forms.EmailField(validators=[EmailValidator(message="Введите корректный email адрес")])

    class Meta:
        model = Client
        fields = ['email', 'first_name', 'last_name', 'middle_name', 'comment']


class MailerCreateForm(forms.ModelForm):
    clients = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=Select2MultipleWidget,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Извлекаем пользователя из kwargs
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['clients'].queryset = Client.objects.filter(owner=user)

        # Получаем все настройки, которые еще не связаны с существующими рассылками
        existing_settings = MailingSettings.objects.filter(mailer__isnull=True)

        # Исключаем существующие настройки из выпадающего списка, а также определяем, что владелец авторизованный юзер
        self.fields['mailing_settings'].queryset = MailingSettings.objects.filter(id__in=existing_settings, owner=user)

        self.fields['email_message'].queryset = EmailMessage.objects.filter(owner=user)

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


class MailingPeriodForm(forms.ModelForm):
    class Meta:
        model = MailingPeriod
        fields = ['daily', 'weekly', 'monthly']

    def clean(self):
        cleaned_data = super().clean()
        daily = cleaned_data.get('daily')
        weekly = cleaned_data.get('weekly')
        monthly = cleaned_data.get('monthly')

        # Проверка на то, что только одно из полей daily, weekly, monthly установлено как True
        if sum([daily, weekly, monthly]) != 1:
            raise ValidationError("Выберите ровно один вариант для периодичности")

