from django.conf.global_settings import EMAIL_HOST_USER
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView

from main.forms import MailerCreateForm, MailingSettingsForm, ClientCreateForm
from main.models import MailingSettings, Client, EmailMessage, Mailer
from main.tasks import send_mail


class IndexListView(ListView):
    model = Client
    template_name = 'main/index.html'
    context_object_name = 'clients'


class ClientListView(ListView):
    model = Client
    context_object_name = 'clients'


class ClientDetailView(DetailView):
    model = Client
    context_object_name = 'client'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(pk=self.kwargs['pk'])
        return queryset


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientCreateForm
    success_url = reverse_lazy('main:client_list')


class ClientUpdateView(UpdateView):
    model = Client
    fields = '__all__'

    def get_success_url(self):
        return reverse('main:client_detail', args=[self.kwargs.get('pk')])


class ClientDeleteView(DeleteView):
    model = Client
    success_url = reverse_lazy('main:client_list')


class EmailMessageListView(ListView):
    model = EmailMessage
    context_object_name = 'mails'


class EmailMessageDetailView(DetailView):
    model = EmailMessage
    context_object_name = 'mail'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(pk=self.kwargs['pk'])
        return queryset


class EmailMessageCreateView(CreateView):
    model = EmailMessage
    success_url = reverse_lazy('main:emailmessage_list')
    fields = '__all__'


class EmailMessageUpdateView(UpdateView):
    model = EmailMessage
    fields = '__all__'

    def get_success_url(self):
        return reverse('main:emailmessage_detail', args=[self.kwargs.get('pk')])


class EmailMessageDeleteView(DeleteView):
    model = EmailMessage
    success_url = reverse_lazy('main:emailmessage_list')


class MailerListView(ListView):
    model = Mailer
    context_object_name = 'mailer_list'


class MailerDetailView(DetailView):
    model = Mailer
    context_object_name = 'mailer'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(pk=self.kwargs['pk'])
        return queryset


class MailerCreateView(CreateView):
    model = Mailer
    form_class = MailerCreateForm
    success_url = reverse_lazy('main:mailer_list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        self.object.clients.set(form.cleaned_data['clients'])
        return HttpResponseRedirect(self.get_success_url())


class MailerUpdateView(UpdateView):
    model = Mailer
    fields = ('clients', 'email_message', 'mailing_settings')

    def get_success_url(self):
        return reverse('main:mailer_detail', args=[self.kwargs.get('pk')])


class MailerDeleteView(DeleteView):
    model = Mailer
    success_url = reverse_lazy('main:mailer_list')


class MailingSettingsListView(ListView):
    model = MailingSettings
    context_object_name = 'settings_list'


class MailingSettingsDetailView(DetailView):
    model = MailingSettings
    context_object_name = 'settings'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(pk=self.kwargs['pk'])
        return queryset


class MailingSettingsCreateView(CreateView):
    model = MailingSettings
    form_class = MailingSettingsForm
    success_url = reverse_lazy('main:mail_settings_list')


class MailingSettingsUpdateView(UpdateView):
    model = MailingSettings
    fields = '__all__'

    def get_success_url(self):
        return reverse('main:mail_settings_detail', args=[self.kwargs.get('pk')])


class MailingSettingsDeleteView(DeleteView):
    model = MailingSettings
    success_url = reverse_lazy('main:mail_settings_list')


def start_mailer(request, mailer_id):
    mailer = Mailer.objects.get(pk=mailer_id)
    if not mailer.mailing_settings.mailing_status.is_started:
        mailer.mailing_settings.mailing_status.is_started = True
        mailer.mailing_settings.mailing_status.is_created = False
        mailer.mailing_settings.mailing_status.save()

        clients_email = [client.email for client in mailer.clients.all()]
        from_email = EMAIL_HOST_USER

        send_mail(mailer, clients_email, mailer.email_message.message_title, mailer.email_message.message_body,
                  mailer.mailing_settings.mailing_date, mailer.mailing_settings.mailing_time,
                  mailer.mailing_settings.mailing_period, from_email)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'mailer/'))


def complete_mailer(request, mailer_id):
    mailer = Mailer.objects.get(pk=mailer_id)
    if mailer.mailing_settings.mailing_status.is_started:
        mailer.mailing_settings.mailing_status.is_started = False
        mailer.mailing_settings.mailing_status.is_complete = True
        mailer.mailing_settings.mailing_status.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'mailer/'))
