from django.urls import path

from medtour.users.views import (
    RegisterOrgAPIView, RegisterUserAPIView, LogoutView, PasswordChangeView,
    PasswordResetChangeView, CreateUserView, PasswordResetActiveView
)

app_name = "medtour.users"
urlpatterns = [
    # API enpoints
    path('register/client/', RegisterUserAPIView.as_view(), name="register-user"),
    path('register/part/', CreateUserView.as_view(), name="register-part"),
    path('register/partner/', RegisterOrgAPIView.as_view(), name="register-org"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('passwordReset/change/', PasswordResetChangeView.as_view(), name='password-restore-change'),
    path('passwordReset/verify/', PasswordResetActiveView.as_view(), name='password-restore-verify'),
]
