from django.urls import path

from .serializers import UserSignUpSerializer
from .views import CreateUserView, VerifyApiView, GetNewVerification, ChangeUserInformationView, ChangeUserPhotoView, \
    LoginView, LoginRefreshView, LogOutView, ForgetPasswordView, ResetPasswordView

urlpatterns = [
    path('signup/', CreateUserView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogOutView.as_view()),
    path('login/refresh/', LoginRefreshView.as_view()),
    path('forget_password/', ForgetPasswordView.as_view()),
    path('reset_password/', ResetPasswordView.as_view()),
    path('verify/', VerifyApiView.as_view()),
    path('new_verify/', GetNewVerification.as_view()),
    path('change_user/', ChangeUserInformationView.as_view()),
    path('change_user_photo/', ChangeUserPhotoView.as_view()),
]