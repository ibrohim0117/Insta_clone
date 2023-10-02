from django.urls import path

from .serializers import UserSignUpSerializer
from .views import CreateUserView

urlpatterns = [
    path('signup/', CreateUserView.as_view())
]