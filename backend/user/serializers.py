from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

from user import models


class ProfileSerializer(serializers.ModelSerializer):
    """What the user may see about their own account: no password hash, no permissions."""

    class Meta:
        model = models.User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'last_login')
        read_only_fields = fields


class RegisterUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=models.User.objects.all(), message='This username is taken.')],
    )
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = models.User
        fields = ('username', 'email', 'password')

    def validate(self, attrs):
        # the validators compare the password with the username and the email too
        try:
            validate_password(attrs['password'], models.User(username=attrs['username'], email=attrs['email']))
        except DjangoValidationError as error:
            raise serializers.ValidationError({'password': list(error.messages)}) from None
        return attrs

    def create(self, validated_data):
        user = models.User(username=validated_data['username'], email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        models.EditorSetting.objects.create(user=user)
        return user


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError('A user with this username and password was not found.')
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        update_last_login(None, user)
        return token


class EditorSettingSerializer(serializers.ModelSerializer):
    value = serializers.JSONField()

    class Meta:
        model = models.EditorSetting
        fields = ('value',)

    def validate_value(self, value):
        if not isinstance(value, dict) or not isinstance(value.get('blocks', []), list):
            raise serializers.ValidationError('Expected an Editor.js document: {"blocks": [...]}.')
        return value
