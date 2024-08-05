import time

import requests
from django.utils import timezone
from datetime import timedelta

from django.db.models import Q
from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User, ResetPassword
from config import settings


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


def user_check_social_account(*, user: User):
    if user.is_social:
        raise Http404(
            "This email is linked with a social account please set the password using reset password first."
        )


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
        raise Http404("The provided link is broken.")


def reset_password_validation(*, reset_password: ResetPassword):
    if reset_password.expires_at < timezone.now():
        raise ValidationError(
            "The provided link has expired, Please request a new password reset email."
        )
    if reset_password.is_blacklisted:
        raise ValidationError(
            "Link already used for reset password, Please request a new password reset email."
        )


class GoogleOAuth2FlowService:
    def __init__(self):
        self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
        self.GOOGLE_GET_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
        self.GOOGLE_OAUTH2_CLIENT_ID = settings.GOOGLE_OAUTH2_CLIENT_ID
        self.GOOGLE_OAUTH2_CLIENT_SECRET = settings.GOOGLE_OAUTH2_CLIENT_SECRET

    def get_access_token(self, *, code: str, redirect_uri: str) -> str:
        # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#obtainingaccesstokens
        data = {
            'code': code,
            'client_id': self.GOOGLE_OAUTH2_CLIENT_ID,
            'client_secret': self.GOOGLE_OAUTH2_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }

        response = requests.post(self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

        if not response.ok:
            raise ValidationError('Failed to obtain access token from Google.')

        access_token = response.json()['access_token']

        return access_token

    def get_user_info(self, *, access_token: str) -> dict:
        response = requests.get(
            self.GOOGLE_GET_USER_INFO_URL, params={"access_token": access_token}
        )

        if not response.ok:
            raise ValidationError("Failed to obtain user info from Google.")

        return response.json()

    @staticmethod
    def create_username_from_google_response(user_data: dict) -> str:
        return f'{user_data.get("given_name", "")}_{user_data.get("family_name", "")}_{str(int(time.time()))}'.lower()


def user_get_or_create_oauth(*, user_profile_data: dict) -> User:
    defaults = user_profile_data
    user, _ = User.objects.get_or_create(email=user_profile_data.get("email"), defaults=defaults)
    return user
