from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    CharField,
    EmailField,
    BooleanField,
    ValidationError,
    SerializerMethodField,
)
from .models import User
from django.db import IntegrityError
from django.utils.dateformat import format


class UserSerializer(ModelSerializer):
    created = SerializerMethodField()
    class Meta:
        model = User
        fields = ("id", "email", "is_email_verified", "created")
        read_only_fields = ("id", "email", "is_email_verified", "created")
        
    def get_created(self, obj):
        return format(obj.created, "M d, Y. P")


class RegisterSerializer(Serializer):
    id = CharField(read_only=True)
    email = EmailField()
    is_email_verified = BooleanField(read_only=True)
    message = CharField(read_only=True)

    def validate(self, data):
        email = data.get("email", None)
        if User.objects.filter(email=email).exists():
            raise IntegrityError("An account with this email already exists.")
        return data

    def save(self, **kwargs):
        return User.objects.create_user(**self.validated_data)

    def to_representation(self, instance):
        user_data = UserSerializer(instance).data
        user_data["message"] = "Check your email for a verification link."
        return user_data
