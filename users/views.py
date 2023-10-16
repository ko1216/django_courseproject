from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView
from django.contrib import messages

from config import settings
from users.forms import UserRegisterForm
from users.models import User


class CustomLoginView(LoginView):
    def form_valid(self, form):
        user = form.get_user()

        if user.email_is_verified:
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Ваш email еще не подтвержден, проверьте почту и перейдите по ссылке')
            return self.form_invalid(form)


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()

        # Генерируем токен для верификации
        token = default_token_generator.make_token(new_user)
        new_user.token = token
        new_user.save()
        uid = urlsafe_base64_encode(force_bytes(new_user.pk))
        token_link = reverse('users:verify_email', kwargs={'uidb64': uid, 'token': token})

        # Отправляем письмо с ссылкой на верификацию
        current_site = get_current_site(self.request)
        mail_subject = f'Подтвердите вашу почту для регистрации на сайте {current_site}'
        message = render_to_string('users/verify_email_message.html', {
            'user': new_user,
            'domain': current_site.domain,
            'token_link': token_link,
        })
        send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [new_user.email])

        return super().form_valid(form)


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        new_user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        new_user = None

    if new_user is not None and new_user.token == token:
        new_user.email_is_verified = True
        new_user.is_active = True
        new_user.save()
        messages.success(request, 'Ваша почта успешно подтверждена.')
        return HttpResponseRedirect(reverse('users:verification_pass'))
    else:
        messages.error(request, 'Ссылка на верификацию недействительна')
        return HttpResponseRedirect(reverse('users:verification_failed'))


def verification_failed(request):
    return render(request, 'users/verification_failed.html')


def verification_pass(request):
    return render(request, 'users/verification_pass.html')


class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_sent.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy('users:password_reset_complete')
    template_name = 'users/password_reset_form.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_done.html'
