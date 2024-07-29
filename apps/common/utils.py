import random
import string
import time
import uuid
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from config import settings


def send_email(*, to: str, subject: str, message: str):
    try:
        email_address = settings.SEND_EMAIL_HOST
        email_password = settings.SEND_EMAIL_PASSWORD
        if email_address is None or email_password is None:
            return False
        send_mail(
            subject=subject,
            message=message,
            from_email=email_address,
            auth_user=email_address,
            auth_password=email_password,
            recipient_list=[to],
            fail_silently=False,
        )
    except Exception as e:
        raise ValidationError(str(e))


def get_unique_identifier_stamp() -> str:
    token = uuid.uuid4()
    timestamp = str(int(time.time()))
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{token}-{timestamp}-{random_chars}"
