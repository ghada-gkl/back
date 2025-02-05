# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()
from rest_framework import serializers
from bson import ObjectId

class ObjectIdField(serializers.Field):
    """Custom serializer field for MongoDB ObjectId."""

    def to_representation(self, value):
        """Convert ObjectId to string."""
        return str(value)

    def to_internal_value(self, data):
        """Convert string to ObjectId."""
        try:
            return ObjectId(data)
        except Exception:
            raise serializers.ValidationError("Invalid ObjectId format.")

class TransactionSerializer(serializers.Serializer):
    id = ObjectIdField(source="_id")
    system_name = serializers.CharField()
    growth = serializers.FloatField()
    file_path = serializers.CharField()
    timestamp = serializers.DateTimeField()

class AlertSerializer(serializers.Serializer):
    id = ObjectIdField(source="_id")
    alert_message = serializers.CharField()
    timestamp = serializers.DateTimeField()
    sid = serializers.CharField()
    code = serializers.CharField()
    transactions = TransactionSerializer(many=True)

class FeedbackSerializer(serializers.Serializer):
    alert_id = ObjectIdField()
    alert_message = serializers.CharField()
    rating = serializers.IntegerField()
    comment = serializers.CharField()
    is_correct = serializers.BooleanField()
    timestamp = serializers.DateTimeField()
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is not returned in the response
        }

    def create(self, validated_data):
        # Hash the password before saving the user
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(
            request=self.context.get('request'),
            email=data['email'],
            password=data['password']
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("Account disabled")
        return {'user': user}

