from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from apps.users.models import User


class CustomAuthBackend(ModelBackend):
    """
    Custom authentication backend.

    Allows users to log in using their email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Overrides the authenticate method to allow users to log in using their email address.
        """
        try:
            user = User.objects.get(Q(email=username) | Q(username=username))
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        """
        Overrides the get_user method to allow users to log in using their email address.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
