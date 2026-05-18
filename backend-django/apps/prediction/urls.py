from django.urls import path
from .views import (
    CreatePredictionTaskView,
    PredictionTaskListView,
    PredictionTaskDetailView
)

urlpatterns = [
    path('create/', CreatePredictionTaskView.as_view(), name='create_prediction_task'),
    path('list/', PredictionTaskListView.as_view(), name='list_prediction_tasks'),
    path('detail/<str:task_id>/', PredictionTaskDetailView.as_view(), name='prediction_task_detail'),
]