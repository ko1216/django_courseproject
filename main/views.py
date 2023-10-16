from random import random

from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView

from blog.models import Blog
from main.forms import MailerCreateForm, MailingSettingsForm, ClientCreateForm, MailingPeriodForm
from main.models import MailingSettings, Client, EmailMessage, Mailer, MailingPeriod, MailingStatus
from main.services import random_choice
from main.tasks import send_mail


class IndexListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'main/index.html'
    context_object_name = 'clients'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailers_count'] = len(Mailer.objects.all())
        context['started_mailers_count'] = len(MailingStatus.objects.filter(is_started=True))
        context['clients'] = len(Client.objects.all())
        context['blogs'] = random_choice(Blog.objects.all())
        return context


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    context_object_name = 'clients'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Client.objects.all()
        else:
            return Client.objects.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    context_object_name = 'client'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(pk=self.kwargs['pk'])
        return queryset

    def get_object(self):
        obj = super().get_object()
        if obj.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Пользователь не является владельцем данной записи')
        return obj


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientCreateForm
    success_url = reverse_lazy('main:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = '__all__'

    def get_success_url(self):
        return reverse('main:client_detail', args=[self.kwargs.get('pk')])

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied('Пользователь не является владельцем данной записи')
        return super().dispatch(request, *args, **kwargs)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('main:client_list')


class EmailMessageListView(LoginRequiredMixin, ListView):
    model = EmailMessage
    context_object_name = 'mails'

    def get_queryset(self):
        if self.request.user.is_staff:
            return EmailMessage.objects.all()
        else:
            return EmailMessage.objects.filter(owner=self.request.user)


class EmailMessageDetailView(LoginRequiredMixin, DetailView):
    model = EmailMessage
    context_object_name = 'mail'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(pk=self.kwargs['pk'])
        return queryset

    def get_object(self):
        obj = super().get_object()
        if obj.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Пользователь не является владельцем данной записи')
        return obj


class EmailMessageCreateView(LoginRequiredMixin, CreateView):
    model = EmailMessage
    success_url = reverse_lazy('main:emailmessage_list')
    fields = ('message_title', 'message_body')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class EmailMessageUpdateView(LoginRequiredMixin, UpdateView):
    model = EmailMessage
    fields = ['message_title', 'message_body']

    def get_success_url(self):
        return reverse('main:emailmessage_detail', args=[self.kwargs.get('pk')])

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Пользователь не является владельцем данной записи')
        return super().dispatch(request, *args, **kwargs)


class EmailMessageDeleteView(LoginRequiredMixin, DeleteView):
    model = EmailMessage
    success_url = reverse_lazy('main:emailmessage_list')


class MailerListView(LoginRequiredMixin, ListView):
    model = Mailer
    context_object_name = 'mailer_list'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Mailer.objects.all()
        else:
            return Mailer.objects.filter(owner=self.request.user)


class MailerDetailView(LoginRequiredMixin, DetailView):
    model = Mailer
    context_object_name = 'mailer'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(pk=self.kwargs['pk'])
        return queryset

    def get_object(self):
        obj = super().get_object()
        if obj.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Пользователь не является владельцем данной записи')
        return obj


class MailerCreateView(LoginRequiredMixin, CreateView):
    model = Mailer
    form_class = MailerCreateForm
    success_url = reverse_lazy('main:mailer_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user  # присваивание владельца для записи

        self.object = form.save(commit=False)
        self.object.save()
        self.object.clients.set(form.cleaned_data['clients'])  # сохранение клиентов со сявзью many to many
        return HttpResponseRedirect(self.get_success_url())


class MailerUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailer
    fields = ('clients', 'email_message', 'mailing_settings')

    def get_success_url(self):
        return reverse('main:mailer_detail', args=[self.kwargs.get('pk')])

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Вы не являетесь владельцем данной записи')
        return super().dispatch(request, *args, **kwargs)


class MailerDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailer
    success_url = reverse_lazy('main:mailer_list')


class MailingSettingsListView(LoginRequiredMixin, ListView):
    model = MailingSettings
    context_object_name = 'settings_list'

    def get_queryset(self):
        if self.request.user.is_staff:
            return MailingSettings.objects.all()
        else:
            return MailingSettings.objects.filter(owner=self.request.user)


class MailingSettingsDetailView(LoginRequiredMixin, DetailView):
    model = MailingSettings
    context_object_name = 'settings'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(pk=self.kwargs['pk'])
        return queryset

    def get_object(self):
        obj = super().get_object()
        if obj.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Вы не являетесь владельцем данной записи')
        return obj


class MailingSettingsCreateView(LoginRequiredMixin, CreateView):
    model = MailingSettings
    form_class = MailingSettingsForm
    success_url = reverse_lazy('main:mail_settings_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        mailing_status, created = MailingStatus.objects.get_or_create(is_created=True)
        form.instance.mailing_status = mailing_status
        return super().form_valid(form)


class MailingSettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = MailingSettings
    form_class = MailingSettingsForm

    def get_success_url(self):
        return reverse('main:mail_settings_detail', args=[self.kwargs.get('pk')])

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Вы не являетесь владельцем данной записи')
        return super().dispatch(request, *args, **kwargs)


class MailingSettingsDeleteView(LoginRequiredMixin, DeleteView):
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


class MailingPeriodListView(LoginRequiredMixin, ListView):
    model = MailingPeriod
    context_object_name = 'period_list'

    def get_queryset(self):
        if self.request.user.is_staff:
            return MailingPeriod.objects.all()
        else:
            return MailingPeriod.objects.filter(owner=self.request.user)


class MailingPeriodDetailView(LoginRequiredMixin, DetailView):
    model = MailingPeriod
    context_object_name = 'period'

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(pk=self.kwargs['pk'])
        return queryset

    def get_object(self):
        obj = super().get_object()
        if obj.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Вы не являетесь владельцем данной записи')
        return obj


class MailingPeriodCreateView(LoginRequiredMixin, CreateView):
    model = MailingPeriod
    success_url = reverse_lazy('main:mail_period_list')
    form_class = MailingPeriodForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingPeriodUpdateView(LoginRequiredMixin, UpdateView):
    model = MailingPeriod
    form_class = MailingPeriodForm

    def get_success_url(self):
        return reverse('main:mail_period_detail', args=[self.kwargs.get('pk')])

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Вы не являетесь владельцем данной записи')
        return super().dispatch(request, *args, **kwargs)


class MailingPeriodDeleteView(LoginRequiredMixin, DeleteView):
    model = MailingPeriod
    success_url = reverse_lazy('main:mail_period_list')
