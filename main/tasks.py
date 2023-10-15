import datetime
import smtplib
from time import sleep

from celery import shared_task
from django.core.mail import EmailMultiAlternatives

from main.models import MessageLog


@shared_task()
def send_mail(mailer,
              emails: list,
              message_title: str,
              message_body: str,
              date,
              time,
              period,
              from_email):
    """
    Функция send_mail берет за основу класс django EmailMultiAlternatives для отправки писем, но обрабатывыает логику
    периодичности отправки писем, а также логику отправки по заданному времени, используя функцию ожидания sleep
    :param mailer: запись из модели Mailer - рассылка в которой указаны клиент, письмо и настройки рассылки
    :param emails: список электронных почт клиентов
    :param message_title: заголовок письма
    :param message_body: тело письма
    :param date: дата начала отправки письма
    :param time: время в которое нужно отправлять письмо
    :param period: периодичность отправки, начиная с заданной даты и времени отправки
    :param from_email: хост email из настроек указанных в настройках проекта
    """
    now_time = datetime.datetime.now()

    try:
        task_datetime = datetime.datetime.combine(date, time)
    except ValueError:
        raise ValueError("Invalid date or time format")

    while True:
        if now_time > task_datetime:
            delay_seconds = (now_time - task_datetime).total_seconds()
        else:
            delay_seconds = (task_datetime - now_time).total_seconds()

        if delay_seconds > 0:
            sleep(delay_seconds)

        try:
            email_message = EmailMultiAlternatives(message_title, message_body, from_email, emails)
            email_message.send()

            # Запись успешной отправки в лог
            log = MessageLog(mailer=mailer, status=True, server_response='Message sent', last_attempt=now_time)
            log.save()
        except smtplib.SMTPException as e:
            # Обработка ошибки при отправке почты
            error_message = f"Failed to send email: {str(e)}"

            # Запись ошибки в лог
            log = MessageLog(mailer=mailer, status=False, server_response=error_message, last_attempt=now_time)
            log.save()

        if period != 'Ежедневно':
            break  # Завершить цикл, если периодичность не "Ежедневно"
        else:
            sleep(60)  # Подождать 60 секунд перед отправкой следующего письма
