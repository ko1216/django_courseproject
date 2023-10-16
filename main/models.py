from django.db import models


NULLABLE = {'blank': True, 'null': True}


class EmailMessage(models.Model):
    message_title = models.CharField(max_length=250, verbose_name='Тема письма')
    message_body = models.TextField(verbose_name='Тело письма')

    def __str__(self):
        return self.message_title

    class Meta:
        verbose_name = 'Сообщение для рассылки'
        verbose_name_plural = 'Сообщения для рассылки'


class Client(models.Model):
    email = models.CharField(max_length=250, verbose_name='email', unique=True)

    first_name = models.CharField(max_length=250, verbose_name='Имя')
    last_name = models.CharField(max_length=250, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=250, verbose_name='Отчество', **NULLABLE)

    comment = models.TextField(verbose_name='Комментарий', **NULLABLE)

    def __str__(self):
        return f'Клиент: {self.last_name} {self.first_name}, email: {self.email}'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class MailingPeriod(models.Model):
    daily = models.BooleanField(default=False, verbose_name='Ежедневно')
    weekly = models.BooleanField(default=False, verbose_name='Еженедельно')
    monthly = models.BooleanField(default=False, verbose_name='Ежемесячно')

    def __str__(self):
        if self.daily:
            return 'Периодичность рассылки: ежедневно'
        elif self.weekly:
            return 'Периодичность рассылки: еженедельно'
        elif self.monthly:
            return 'Периодичность рассылки: ежемесячно'
        else:
            return 'Периодичность не задана'

    class Meta:
        verbose_name = 'Периодичность'
        verbose_name_plural = 'Периодичности'


class MailingStatus(models.Model):
    is_created = models.BooleanField(default=True, verbose_name='Рассылка создана', **NULLABLE)
    is_started = models.BooleanField(default=False, verbose_name='Рассылка запущена', **NULLABLE)
    is_complete = models.BooleanField(default=False, verbose_name='Рассылка завершена', **NULLABLE)

    def __str__(self):
        if self.is_created:
            return 'Статус рассылки: создана'
        elif self.is_started:
            return 'Статус рассылки: запущена'
        elif self.is_complete:
            return 'Статус рассылки: завершена'
        else:
            return 'Статус рассылки: не определена'

    class Meta:
        verbose_name = 'Статус рассылки'
        verbose_name_plural = 'Статусы рассылки'


class MailingSettings(models.Model):
    mailing_date = models.DateField(verbose_name='Дата начала рассылки')
    mailing_time = models.TimeField(verbose_name='Время для рассылки')
    mailing_period = models.ForeignKey(MailingPeriod, on_delete=models.CASCADE, verbose_name='Периодичность рассылки')
    mailing_status = models.ForeignKey(MailingStatus, on_delete=models.CASCADE, verbose_name='Статус рассылки')

    def __str__(self):
        return f'Время рассылки: {self.mailing_time}, периодичность: {self.mailing_period}, статус: {self.mailing_status}'

    class Meta:
        verbose_name = 'Настройки рассылки'
        verbose_name_plural = 'Настройки рассылок'


class Mailer(models.Model):
    email_message = models.ForeignKey(EmailMessage, on_delete=models.CASCADE, verbose_name='Письмо для рассылки')
    clients = models.ManyToManyField(Client, verbose_name='Клиенты')
    mailing_settings = models.ForeignKey(MailingSettings, on_delete=models.CASCADE, verbose_name='Настройки рассылки')
    # message_log = models.ForeignKey(MessageLog, on_delete=models.CASCADE, verbose_name='Логи рассылки', **NULLABLE)

    def __str__(self):
        client_emails = ', '.join([client.email for client in self.clients.all()])
        return f'Клиенты: {client_emails}, Письмо: {self.email_message.message_title}, ' \
               f'{self.mailing_settings.mailing_period}, ' \
               f'Дата и время начала рассылки: {self.mailing_settings.mailing_date} {self.mailing_settings.mailing_time}'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class MessageLog(models.Model):
    last_attempt = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время последней попытки')
    status = models.BooleanField(default=False, verbose_name='Статус отправки')
    server_response = models.TextField(verbose_name='Ответ почтового сервера', **NULLABLE)
    mailer = models.ForeignKey(Mailer, on_delete=models.CASCADE, verbose_name='Рассылка', **NULLABLE)

    def __str__(self):
        return f'время попытки: {self.last_attempt}, статус {self.status}'

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'
