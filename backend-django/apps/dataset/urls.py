from django.urls import path
from .views import DatasetDeleteView, DatasetUploadView, DatasetListView

urlpatterns = [
    path('upload/', DatasetUploadView.as_view(), name='dataset-upload'),
    path('list/', DatasetListView.as_view(), name='dataset-list'),
    path('delete/<str:dataset_id>/', DatasetDeleteView.as_view(), name='dataset-delete'),
]