from django.urls import path
from .views import ModelUploadView, ModelListView, ModelDeleteView

urlpatterns = [
    path("upload/", ModelUploadView.as_view(), name="model-upload"),
    path("list/", ModelListView.as_view(), name="model-list"),
    path("delete/<str:model_id>/", ModelDeleteView.as_view(), name="model-delete")
]