from django.contrib import admin

from main.models import Client, Mailer, MailingSettings, MessageLog, EmailMessage


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'last_name', 'first_name', 'pk',)


@admin.register(EmailMessage)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('message_title', 'pk',)


@admin.register(Mailer)
class MailerAdmin(admin.ModelAdmin):
    list_display = ('email_message', 'mailing_settings',)
    list_filter = ('email_message',)


@admin.register(MailingSettings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('mailing_date', 'mailing_time', 'mailing_period', 'mailing_status',)


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('server_response', 'last_attempt')
    list_filter = ('server_response',)
