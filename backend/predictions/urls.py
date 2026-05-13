from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import PredictionTaskListCreateView, PredictionTaskDetailView

urlpatterns = [
    path('', csrf_exempt(PredictionTaskListCreateView.as_view()), name='prediction-list-create'),
    path('<int:pk>/', csrf_exempt(PredictionTaskDetailView.as_view()), name='prediction-detail'),
]
