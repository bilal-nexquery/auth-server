from django.utils import timezone
from datetime import timedelta

from django.db.models import Q
from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User, ResetPassword


def user_create(*, email: str, username: str, password: str) -> User:
    user = User(email=email, username=username)
    user.set_password(password)
    user.save()
    return user


def user_get(*, username: str) -> User:
    try:
        user = User.objects.get(Q(email=username) | Q(username=username))
        return user
    except User.DoesNotExist:
        raise Http404("No user with this email or username exists.")


def user_check_password(*, user: User, password: str) -> bool:
    return user.check_password(password)


def get_tokens_for_user(*, user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def reset_password_create_or_update(*, unique_identifier: str, user: User):
    defaults = {
        "token": unique_identifier,
        "created_or_updated_at": timezone.now(),
        "expires_at": timezone.now() + timedelta(minutes=30),
        "user": user,
        "is_blacklisted": False,
    }
    ResetPassword.objects.update_or_create(user=user, defaults=defaults)


def get_email_content_for_forgot_password(
    *, user: User, reset_password_link: str
) -> tuple[str, str]:
    subject = "Subject : Reset Your Password"
    message = (
        f"Dear {user.username},\n\n"
        f"We have received a request to reset your password.\n"
        f"To reset your password, please click on the following link:\n{reset_password_link}\n\n"
        f"If you did not request to reset your password, "
        f"Please ignore this email and your account will remain unchanged.\n"
        f"Please note that the link will expire in 30 Minutes. If the link expires, "
        f"you will need to request another password reset.\n\n"
        f"Thank you,\n\nOperations Team."
    )
    return subject, message


def reset_password_get(*, token: str) -> ResetPassword:
    try:
        reset_password = ResetPassword.objects.get(token=token)
        return reset_password
    except ResetPassword.DoesNotExist:
        raise Http404("The provided link is invalid.")


def reset_password_validation(*, reset_password: ResetPassword):
    if reset_password.expires_at < timezone.now():
        raise ValidationError(
            "The provided link has expired, Please request a new password reset email."
        )
    if reset_password.is_blacklisted:
        raise ValidationError(
            "Link already used for reset password, Please request a new password reset email."
        )
