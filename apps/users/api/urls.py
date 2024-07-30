from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.api.views import UserCreateApi, UserLoginApi, UserListApi, UserForgotPasswordApi, \
    UserResetPasswordValidateAPI, UserResetPasswordApi

urlpatterns = [
    path("register/", UserCreateApi.as_view(), name="register"),
    path("login/", UserLoginApi.as_view(), name="login"),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', UserListApi.as_view(), name="user-list"),
    path("forgot-password/", UserForgotPasswordApi.as_view(), name="forgot-password"),
    path("validate/reset-password/<str:token>/", UserResetPasswordValidateAPI.as_view(), name="validate-reset_password"),
    path("reset-password/<str:token>/", UserResetPasswordApi.as_view(), name="reset-password"),
]
