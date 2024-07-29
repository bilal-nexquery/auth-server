from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.api.views import UserCreateApi, UserLoginApi, UserListApi, UserForgotPasswordApi

urlpatterns = [
    path("register/", UserCreateApi.as_view(), name="register"),
    path("login/", UserLoginApi.as_view(), name="login"),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserListApi.as_view(), name="user_list"),
    path("forgot-password/", UserForgotPasswordApi.as_view(), name="forgot_password"),
]
