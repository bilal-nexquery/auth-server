from django.urls import path, include

from apps.users.api.views import UserCreateApi

urlpatterns = [
    path("register/", UserCreateApi.as_view(), name="register"),
]
