from django.urls import path, include
from django.contrib import admin
from django.http import HttpResponse


def home(request):
    return HttpResponse('Freight Rate Predicting System backend is running.')

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/models/', include('mlmodels.urls')),
    path('api/predictions/', include('predictions.urls')),
]
