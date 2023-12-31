import uuid
from datetime import datetime, timedelta
import random

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import BaseModel

ORDINARY_USER = 'ordinary_user'
MANAGER = 'manager'
ADMIN = 'admin'

VIA_EMAIL = 'via_email'
VIA_PHONE = 'via_phone'

NEW = 'new'
CODE_VERIFIED = 'code_verified'
DONE = 'done'
PHOTO_STEP = 'photo_step'

PHONE_EXPIRE = 2
EMAIL_EXPIRE = 5


class User(AbstractUser, BaseModel):
    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )

    AUTH_TYPE_CHOICES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )

    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_STEP, PHOTO_STEP)
    )

    user_roles = models.CharField(max_length=255, choices=USER_ROLES, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=255, choices=AUTH_TYPE_CHOICES)
    auth_status = models.CharField(max_length=255, choices=AUTH_STATUS, default=NEW)
    email = models.EmailField(null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True, unique=True)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png', 'jpeg'])])

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint(0, 100) % 10) for _ in range(4)])
        UserConfirmation.objects.create(user_id=self.id, verify_type=verify_type, code=code)
        return code

    def check_username(self):
        if not self.username:
            temp_username = f"instagram-{uuid.uuid4().__str__().split('-')[-1]}"
            self.username = temp_username

    def check_email(self):
        if self.email:
            normalize_email = self.email.lower()
            self.email = normalize_email

    def check_pass(self):
        if not self.password:
            temp_password = f"instagram-{uuid.uuid4().__str__().split('-')[-1]}"
            self.username = temp_password

    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        data = {
            "refresh_token": str(refresh),
            "access": str(refresh.access_token)
        }
        return data

    def clean(self):
        self.check_email()
        self.check_pass()
        self.check_username()
        self.hashing_password()

    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)


class UserConfirmation(BaseModel):
    TYPE_CHOICES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )

    verify_type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    code = models.CharField(max_length=4)
    user = models.ForeignKey('user.User', models.CASCADE, related_name='verify_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL:
            self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
        else:
            self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
        super(UserConfirmation, self).save(*args, **kwargs)



