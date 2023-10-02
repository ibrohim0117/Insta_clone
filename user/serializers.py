from shared.utility import check_email_or_phone_num
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
        self.fields['email_or_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status'
        )

    def validate(self, data):
        super(UserSignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    def create(self, validated_data):
        user = super(UserSignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            # send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            # send_phone(user.phone_number, code)
        user.save()

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_or_phone_number')).lower()   # userdan kelgan ma'lumotni oldik
        input_type = check_email_or_phone_num(user_input)
        # print("user_input", user_input)
        # print("input_type", input_type)
        if input_type == 'email':
            data = {
                'success': True,
                'email': user_input,
                'auth_type': VIA_EMAIL
            }
        elif input_type == 'phone':
            data = {
                'success': True,
                'phone': user_input,
                'auth_type': VIA_PHONE
            }
        else:
            data = {
                'success': False,
                'message': "Invalid email or phone number"
            }
            raise ValidationError(data)
        print(data)
        return data
