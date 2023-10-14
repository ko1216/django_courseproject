from django.urls import path

from main.apps import MainConfig
from main.views import IndexListView, ClientListView, ClientCreateView, ClientDetailView, ClientDeleteView, \
    ClientUpdateView, EmailMessageListView, EmailMessageCreateView, EmailMessageDetailView, EmailMessageDeleteView, \
    EmailMessageUpdateView, MailerListView, MailerCreateView, MailerDetailView, MailerDeleteView, MailerUpdateView, \
    MailingSettingsListView, MailingSettingsCreateView, MailingSettingsDetailView, MailingSettingsDeleteView, \
    MailingSettingsUpdateView

app_name = MainConfig.name


urlpatterns = [
    path('', IndexListView.as_view(), name='index'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('create_client/', ClientCreateView.as_view(), name='client_form'),
    path('<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('delete/<int:pk>', ClientDeleteView.as_view(), name='client_delete'),
    path('update/<int:pk>', ClientUpdateView.as_view(), name='client_update'),
    path('mails/', EmailMessageListView.as_view(), name='emailmessage_list'),
    path('create_mail/', EmailMessageCreateView.as_view(), name='emailmessage_form'),
    path('mail/<int:pk>/', EmailMessageDetailView.as_view(), name='emailmessage_detail'),
    path('mail/delete/<int:pk>', EmailMessageDeleteView.as_view(), name='emailmessage_delete'),
    path('mail/update/<int:pk>', EmailMessageUpdateView.as_view(), name='emailmessage_update'),
    path('mailer/', MailerListView.as_view(), name='mailer_list'),
    path('create_mailer/', MailerCreateView.as_view(), name='mailer_form'),
    path('mailer/<int:pk>/', MailerDetailView.as_view(), name='mailer_detail'),
    path('mailer/delete/<int:pk>', MailerDeleteView.as_view(), name='mailer_delete'),
    path('mailer/update/<int:pk>', MailerUpdateView.as_view(), name='mailer_update'),
    path('mail_settings/', MailingSettingsListView.as_view(), name='mail_settings_list'),
    path('create_mail_settings/', MailingSettingsCreateView.as_view(), name='mail_settings_form'),
    path('mail_settings/<int:pk>/', MailingSettingsDetailView.as_view(), name='mail_settings_detail'),
    path('mail_settings/delete/<int:pk>', MailingSettingsDeleteView.as_view(), name='mail_settings_delete'),
    path('mail_settings/update/<int:pk>', MailingSettingsUpdateView.as_view(), name='mail_settings_update'),
]
