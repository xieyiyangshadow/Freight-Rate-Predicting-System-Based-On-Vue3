from django.urls import path
from .views import (
    CreatePredictionTaskView,
    PredictionTaskListView,
    PredictionTaskDetailView
)
from .views import DeletePredictionTaskView

urlpatterns = [
    path('create/', CreatePredictionTaskView.as_view(), name='create_prediction_task'),
    path('list/', PredictionTaskListView.as_view(), name='list_prediction_tasks'),
    path('detail/<str:task_id>/', PredictionTaskDetailView.as_view(), name='prediction_task_detail'),
    path('delete/<str:task_id>/', DeletePredictionTaskView.as_view(), name='prediction_task_delete'),
]