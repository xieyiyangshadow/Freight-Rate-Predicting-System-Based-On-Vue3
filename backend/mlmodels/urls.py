from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import MLModelListCreateView, MLModelDetailView, DatasetListCreateView, DatasetDetailView

urlpatterns = [
    path('', csrf_exempt(MLModelListCreateView.as_view()), name='mlmodel-list-create'),
    path('<int:pk>/', csrf_exempt(MLModelDetailView.as_view()), name='mlmodel-detail'),
    path('datasets/', csrf_exempt(DatasetListCreateView.as_view()), name='dataset-list-create'),
    path('datasets/<int:pk>/', csrf_exempt(DatasetDetailView.as_view()), name='dataset-detail'),
]
