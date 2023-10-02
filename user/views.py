from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from .serializers import UserSignUpSerializer
from .models import User


class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = (permissions.AllowAny, )


