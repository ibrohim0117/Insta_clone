from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from shared.utility import check_email_or_phone_num, send_email, check_user_type
from .models import User, UserConfirmation, VIA_PHONE, VIA_EMAIL, NEW, CODE_VERIFIED, DONE, PHOTO_STEP
from rest_framework import exceptions
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied


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


class ChangeUserPhoto(serializers.Serializer):    # noqa
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heic', 'heif'])])

    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_STEP
            instance.save()
        return instance


class LoginSerializer(TokenObtainSerializer):    # noqa

    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)

    def auth_validate(self, data):
        user_input = data.get('userinput')
        if check_user_type(user_input) == 'username':
            username = user_input
        elif check_user_type(user_input) == 'email':
            user = self.get_user(email__exact=user_input)
            username = user.username
        elif check_user_type(user_input) == 'phone':
            user = self.get_user(phone_number=user_input)
            username = user.username
        else:
            data = {
                'success': True,
                'message': 'Siz email username yoki telefon raqami kiritishingiz kerak!'
            }
            raise ValidationError(data)

        authentication_kwargs = {
            self.username_field: username,
            'password': data['password']
        }

        # user statusini tekshirish
        current_user = User.objects.filter(username__iexact=username).first()
        print(current_user)
        if current_user is not None and current_user.auth_status in [NEW, CODE_VERIFIED]:
            raise ValidationError(
                {
                    'success': False,
                    'message': "Siz ro'yhatdan to'liq o'tmagansiz"
                }
            )
        user = authenticate(**authentication_kwargs)
        if user is not None:
            self.user = user
        else:
            raise ValidationError(
                {
                    'success': False,
                    'message': 'Uzur sizning kiritgan login parolingiz xato qaytadan urining!'
                }
            )

    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE, PHOTO_STEP]:
            raise PermissionDenied("Siz login qilaolmaysiz ruxsatingiz yo'q")
        data = self.user.token()
        data['auth_status'] = self.user.auth_status
        data['full_name'] = self.user.full_name
        return data

    def get_user(self, **kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise ValidationError(
                {'message': 'Bunday user topilmadi!'}
            )
        return users.first()


class LoginRefreshSerializer(TokenRefreshSerializer):   # noqa

    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data

class LogOutSerializer(serializers.Serializer):   # noqa
    refresh = serializers.CharField()










