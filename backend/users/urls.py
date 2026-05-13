from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import RegisterView, LoginView

urlpatterns = [
    path('register/', csrf_exempt(RegisterView.as_view()), name='register'),
    path('login/', csrf_exempt(LoginView.as_view()), name='login'),
]
