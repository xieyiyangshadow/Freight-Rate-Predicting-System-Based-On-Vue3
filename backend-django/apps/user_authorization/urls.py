from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegisterView,
    UserLoginView,
    UserInfoView,
    UserLogoutView,
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('info/', UserInfoView.as_view(), name='user-info'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
]