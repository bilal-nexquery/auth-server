from django.http import Http404
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from apps.common.utils import send_email, get_unique_identifier_stamp
from apps.common.validators import WhiteSpaceValidator, PasswordRegexValidator
from apps.core.authentication import CustomAuthBackend
from apps.core.views import BaseAPIView
from apps.users.services import user_create, user_get, user_check_password, get_tokens_for_user, \
    get_email_content_for_forgot_password, reset_password_create_or_update, reset_password_get, \
    reset_password_validation
from config import settings


class UserCreateApi(BaseAPIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=True, allow_blank=False, allow_null=False)
        username = serializers.CharField(
            max_length=255,
            required=True,
            allow_blank=False,
            allow_null=False,
            validators=[WhiteSpaceValidator()],
        )
        password = serializers.CharField(
            max_length=255,
            required=True,
            allow_blank=False,
            allow_null=False,
            validators=[PasswordRegexValidator()],
        )

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_create(**serializer.validated_data)
        return self.send_response(
            success=True,
            code="201",
            description="User created successfully",
            status_code=status.HTTP_201_CREATED,
        )


class UserLoginApi(BaseAPIView):
    custom_auth_backend = CustomAuthBackend

    class InputSerializer(serializers.Serializer):
        username = serializers.CharField(required=True, allow_blank=False, allow_null=False)
        password = serializers.CharField(required=True, allow_blank=False, allow_null=False)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_get(username=serializer.validated_data.get("username"))
        if not user_check_password(user=user, password=serializer.validated_data.get("password")):
            raise Http404("Incorrect password for this account")
        self.custom_auth_backend().authenticate(request, **serializer.validated_data)
        tokens = get_tokens_for_user(user=user)
        return self.send_response(
            success=True,
            code="200",
            description=tokens,
            status_code=status.HTTP_200_OK,
        )


class UserListApi(BaseAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return self.send_response(
            success=True,
            code="201",
            description="User created successfully",
            status_code=status.HTTP_201_CREATED,
        )


class UserForgotPasswordApi(BaseAPIView):
    class InputSerializer(serializers.Serializer):
        username = serializers.CharField(required=True, allow_blank=False, allow_null=False)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_get(username=serializer.validated_data.get("username"))
        unique_identifier = get_unique_identifier_stamp()
        reset_password_create_or_update(unique_identifier=unique_identifier, user=user)
        reset_password_link = f"{settings.FRONTEND_BASE_URL}/reset-password/{unique_identifier}/"
        subject, message = get_email_content_for_forgot_password(user=user, reset_password_link=reset_password_link)
        send_email(to=user.email, subject=subject, message=message)
        return self.send_response(
            success=True,
            code="201",
            description="Reset password link sent successfully, Please check your email.",
            status_code=status.HTTP_201_CREATED,
        )


class UserResetPasswordValidateAPI(BaseAPIView):
    def get(self, request, token: str):
        reset_password = reset_password_get(token=token)
        reset_password_validation(reset_password=reset_password)
        return self.send_response(
            success=True,
            code="200",
            description="Link validated successfully",
            status_code=status.HTTP_200_OK,
        )


class UserResetPasswordApi(BaseAPIView):
    class InputSerializer(serializers.Serializer):
        password = serializers.CharField(required=True, allow_blank=False, allow_null=False,
                                         validators=[PasswordRegexValidator()])

    def post(self, request, token: str):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_password = reset_password_get(token=token)
        reset_password_validation(reset_password=reset_password)
        reset_password.user.set_password(serializer.validated_data.get("password"))
        reset_password.is_blacklisted = True
        reset_password.save()
        reset_password.user.save()
        return self.send_response(
            success=True,
            code="200",
            description="Password reset successfully, Please login with new password",
            status_code=status.HTTP_200_OK,
        )
