from django.urls import path
from .views import DatasetDeleteView, DatasetUploadView, DatasetListView, DatasetDetailView

urlpatterns = [
    path('upload/', DatasetUploadView.as_view(), name='dataset-upload'),
    path('list/', DatasetListView.as_view(), name='dataset-list'),
    path('detail/<str:dataset_id>/', DatasetDetailView.as_view(), name='dataset-detail'),
    path('delete/<str:dataset_id>/', DatasetDeleteView.as_view(), name='dataset-delete'),
]