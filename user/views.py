from datetime import datetime

from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSignUpSerializer, VerifyCodeSerializer
from .models import User, DONE, CODE_VERIFIED, NEW


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


