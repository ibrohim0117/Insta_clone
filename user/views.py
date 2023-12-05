from datetime import datetime

from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, generics
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from shared.utility import send_email
from .serializers import UserSignUpSerializer, VerifyCodeSerializer, ChangeUserInformation, ChangeUserPhoto, \
    LoginSerializer, LoginRefreshSerializer
from .models import User, DONE, CODE_VERIFIED, NEW, VIA_EMAIL, VIA_PHONE


class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = (permissions.AllowAny, )


class VerifyApiView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        request_body=VerifyCodeSerializer,
        responses={200: 'OK', 400: 'Bad Request'},
    )
    def post(self, request, *args, **kwargs):
        user = self.request.user
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data.get('code')
            self.check_verify(user, code)
            return Response(
                data={
                    'success': True,
                    'auth_status': user.auth_status,
                    'access': user.token()['access'],
                    'refresh': user.token()['refresh_token']
                }
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def check_verify(user, code):
        print(user)
        print(code)
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        print(verifies)
        if not verifies.exists():
            data = {
                'message': 'Tasdiqlash kodi xato yoki eskirgan'
            }
            raise ValidationError(data)
        verifies.update(is_confirmed=True)
        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True


class GetNewVerification(APIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
        else:
            data = {
                'message': 'Email yoki telefon raqami xato'
            }
            raise ValidationError(data)
        return Response(
            {
                'success': True,
                'message': 'Tasdiqlash kodingiz qaytadan yuborildi!'
            }
        )

    @staticmethod
    def check_verification(user):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
        if verifies.exists():
            data = {
                'message': 'Kodingiz hali ishlatish uchun yaroqli'
            }
            raise ValidationError(data)


class ChangeUserInformationView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangeUserInformation
    permission_classes = (permissions.IsAuthenticated, )
    http_method_names = ['patch', 'put']

    def get_object(self):
        print(self.request.user)
        print(self.request.user.id)
        return get_object_or_404(User, id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).update(request, *args, **kwargs)
        data = {
            'success': True,
            'message': 'User update success',
            'auth_status': self.request.user.auth_status
        }
        return Response(data, status=200)

    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).partial_update(request, *args, **kwargs)
        data = {
            'success': True,
            'message': 'User update success',
            'auth_status': self.request.user.auth_status,
            'data': self.request.data
        }
        return Response(data, status=200)


class ChangeUserPhotoView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        request_body=ChangeUserPhoto,
        responses={200: 'OK', 400: 'Bad Request'},
    )
    def put(self, request, *args, **kwargs):
        serializer = ChangeUserPhoto(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.update(user, serializer.validated_data)
            data = {
                'success': True,
                'message': "Rasm fuvofaqqiyatli uzgardi!"
            }
            return Response(data)
        return Response(
            serializer.errors, status=400
        )

class LoginView(TokenObtainPairView):     # noqa
    serializer_class = LoginSerializer


class LoginRefreshView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer



