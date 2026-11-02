from django.urls import path

from accounts.presentation.views import LoginView, RefreshView, RegistrationView

urlpatterns = [
    path("registration", RegistrationView.as_view(), name="registration"),
    path("login", LoginView.as_view(), name="login"),
    path("refresh", RefreshView.as_view(), name="token-refresh"),
]
