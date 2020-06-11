from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        '''Creates new user with encrypted password'''
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data, **kwargs):
        password = validated_data.pop('password')
        user = super().update(instance, validated_data, **kwargs)

        if password:
            user.set_password(password)
            user.save()

        return user


class UserTokenSerializer(serializers.Serializer):
    '''Serializer for token creation'''
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, raw_data):
        '''Validates if the user exists'''
        email = raw_data.get('email')
        password = raw_data.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        if not user:
            msg = _('Authentication failed, try again')
            raise serializers.ValidationError(msg, code='authentication')

        raw_data['user'] = user
        return raw_data
