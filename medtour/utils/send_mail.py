from django.conf import settings
from django.core import mail
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_email(data):
    subject = 'MedTour Email Verification'
    # html_message = render_to_string(
    #     'auth/activate.html', {'url': data['url'], 'firstname': data['firstname'],
    #     'lastname': data['lastname'], 'text': data['text']})
    message = _('Your code is: {}').format(str(data['code']))
    # plain_message = strip_tags(message1)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = data['to_email']
    # send_mail(subject=data['email_subject'],message=data['email_body'],from_email=EMAIL_HOST_USER,recipient_list=[data['to_email']])
    try:
        mail.send_mail(subject, message, from_email, [to])
    except Exception as e:
        raise ValidationError(f"Ошибка {e}")


# Универсальная функция отправки сообщений
# TODO: Добавить аннотацию Celery и подключить к URL
def send_email_html(to: list, subject: str, template_name: str, context: dict, **kwargs):
    html_content = render_to_string(template_name, context)
    message = EmailMessage(subject, html_content, to=to, **kwargs)
    message.content_subtype = "html"
    try:
        return message.send()
    except Exception as e:
        raise ValidationError(f"Ошибка {e}")
