from rest_framework import serializers, status

from apps.common.validators import WhiteSpaceValidator
from apps.core.views import BaseAPIView
from apps.users.services import user_create


class UserCreateApi(BaseAPIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=True, allow_blank=False, allow_null=False)
        username = serializers.CharField(
            max_length=255, required=True, allow_blank=False, allow_null=False, validators=[WhiteSpaceValidator()]
        )
        password = serializers.CharField(
            max_length=255, required=True, allow_blank=False, allow_null=False
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
