import re

from rest_framework import serializers


class WhiteSpaceValidator:
    """
    This method is automatically called by drf with the value of field whenever an object of
    this class is instantiated.
    """

    def __call__(self, value):
        if re.search(r'\s+', value):
            message = "whitespace are not allowed in this field"
            raise serializers.ValidationError(message)