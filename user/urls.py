from django.urls import path

from .serializers import UserSignUpSerializer
from .views import CreateUserView, VerifyApiView, GetNewVerification

urlpatterns = [
    path('signup/', CreateUserView.as_view()),
    path('verify/', VerifyApiView.as_view()),
    path('new_verify/', GetNewVerification.as_view()),
]