from django.db.models import Q
from django.http import Http404
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


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
