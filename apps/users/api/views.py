import json

import requests
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated

from apps.common.validators import WhiteSpaceValidator, PasswordRegexValidator
from apps.core.authentication import CustomAuthBackend
from apps.core.views import BaseAPIView
from apps.users.services import user_create, user_get, user_check_password, get_tokens_for_user
from config.settings import BACKEND_BASE_URL


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
        username = serializers.CharField(required=True)
        password = serializers.CharField(required=True)

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_get(username=serializer.validated_data.get("username"))
        if not user_check_password(user=user, password=serializer.validated_data.get("password")):
            return self.send_response(
                success=False,
                code="404",
                message="Not found",
                description="Incorrect password",
                status_code=status.HTTP_404_NOT_FOUND,
            )
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
