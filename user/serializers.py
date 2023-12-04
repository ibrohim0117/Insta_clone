from django.contrib.auth.password_validation import validate_password

from shared.utility import check_email_or_phone_num, send_email
from .models import User, UserConfirmation, VIA_PHONE, VIA_EMAIL, NEW, CODE_VERIFIED, DONE, PHOTO_STEP
from rest_framework import exceptions
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserSignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_type = serializers.CharField(read_only=True, required=False)
    auth_status = serializers.CharField(read_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super(UserSignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('id', 'auth_type', 'auth_status')
        
    def create(self, validated_data):
        user = super(UserSignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            print(code)
        user.save()
        return user

    def validate(self, attrs):
        super(UserSignUpSerializer, self).validate(attrs)
        data = self.auth_validate(attrs)
        return data

    @staticmethod
    def auth_validate(attrs):
        user_input = str(attrs.get('email_phone_number')).lower()
        input_type = check_email_or_phone_num(user_input)
        print(input_type, user_input)
        if input_type == 'email':
            data = {
                'email': user_input,
                'auth_type': VIA_EMAIL
            }
        elif input_type == 'phone':
            data = {
                'phone_number': user_input,
                'auth_type': VIA_PHONE
            }
        else:
            data = {
                'success': False,
                'message': 'Telefon raqam yoki email kiritishingiz kerak!'
            }
            raise ValidationError(data)

        return data

    def validate_email_phone_number(self, value):  # noqa
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            data = {
                'success': False,
                'message': 'Bu emaildan oldin foydalanilgan!'
            }
            raise ValidationError(data)

        elif value and User.objects.filter(phone_number=value).exists():
            data = {
                'success': False,
                'message': 'Bu telefon raqamdan oldin foydalanilgan!'
            }
            raise ValidationError(data)

        return value

    def to_representation(self, instance):
        data = super(UserSignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data


class VerifyCodeSerializer(serializers.Serializer):       # noqa
    code = serializers.CharField(max_length=4, write_only=True)


class ChangeUserInformation(serializers.Serializer):      # noqa
    first_name = serializers.CharField(max_length=15, required=True, write_only=True)
    last_name = serializers.CharField(max_length=15, required=True, write_only=True)
    username = serializers.CharField(max_length=15, required=True, write_only=True)
    password = serializers.CharField(max_length=255, required=True, write_only=True)
    confirm_password = serializers.CharField(max_length=255, required=True, write_only=True)

    def validate(self, attrs):
        password = attrs.get('password', None)
        confirm_password = attrs.get('confirm_password', None)
        if password != confirm_password:
            data = {
                'success': False,
                'message': 'Parolingiz va tasdiqlash parolingiz bir biriga teng emas!'
            }
            raise ValidationError(data)
        if password:
            validate_password(password)
            validate_password(confirm_password)

        return attrs

    def validate_username(self, username):  # noqa
        if len(username) < 5 or len(username) > 35:
            data = {
                'success': False,
                'message': "Username 5 dan kam 15 dan ko'p bolmasligi kerak!"
            }
            raise ValidationError(data)

        return username

    def validate_first_name(self, first_name):  # noqa
        if len(first_name) < 5 or len(first_name) > 35:
            data = {
                'success': False,
                'message': "Ismingiz 5 dan kam 15 dan ko'p bolmasligi kerak!"
            }
            raise ValidationError(data)

        if first_name.isdigit():
            data = {
                'success': False,
                'message': "Ismingiz faqat harflardan tashkil topgan bolishi kerak"
            }
            raise ValidationError(data)

        return first_name

    def validate_last_name(self, last_name):  # noqa
        if len(last_name) < 5 or len(last_name) > 35:
            data = {
                'success': False,
                'message': "Familyangiz 5 dan kam 15 dan ko'p bolmasligi kerak!"
            }
            raise ValidationError(data)
        if last_name.isdigit():
            data = {
                'success': False,
                'message': "Familyangiz faqat harflardan tashkil topgan bolishi kerak"
            }
            raise ValidationError(data)

        return last_name

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.password = validated_data.get('password', instance.password)
        instance.username = validated_data.get('username', instance.username)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance




