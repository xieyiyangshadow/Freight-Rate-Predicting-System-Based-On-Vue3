from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import PredictionTask
from .serializers import PredictionTaskSerializer
import os
from django.utils import timezone
import json
from django.contrib.auth import get_user_model
from freight.request_utils import extract_user_id
from freight.task_queue import enqueue_prediction

class PredictionTaskListCreateView(generics.ListCreateAPIView):
    queryset = PredictionTask.objects.all()
    serializer_class = PredictionTaskSerializer
    authentication_classes = []
    permission_classes = [__import__('rest_framework.permissions', fromlist=['AllowAny']).AllowAny]

    def get_queryset(self):
        user_id = extract_user_id(self.request)
        queryset = super().get_queryset().order_by('-id')
        return queryset.filter(owner_id=user_id) if user_id else queryset.none()

    def perform_create(self, serializer):
        user_id = extract_user_id(self.request)
        user_model = get_user_model()
        owner = user_model.objects.filter(id=user_id).first() if user_id else None
        if owner is None:
            raise ValidationError({'detail': '请先登录后再创建预测任务'})

        selected_models = list(serializer.validated_data.get('models_used', []))
        allowed_models = [model for model in selected_models if model.owner_id == owner.id and model.status == 'completed']
        if not allowed_models:
            raise ValidationError({'detail': '请选择至少一个属于当前用户且状态为训练完成的模型'})

        instance = serializer.save(owner=owner, status='pending')
        instance.models_used.set(allowed_models)
        base = os.path.join('predictions_storage', str(instance.id))
        os.makedirs(base, exist_ok=True)
        instance.output_folder = base
        instance.status = 'running'
        instance.save(update_fields=['output_folder', 'status'])
        enqueue_prediction(instance.id, base, [model.id for model in allowed_models])

class PredictionTaskDetailView(generics.RetrieveDestroyAPIView):
    queryset = PredictionTask.objects.all()
    serializer_class = PredictionTaskSerializer
    authentication_classes = []
    permission_classes = [__import__('rest_framework.permissions', fromlist=['AllowAny']).AllowAny]

    def get_queryset(self):
        user_id = extract_user_id(self.request)
        queryset = super().get_queryset().order_by('-id')
        return queryset.filter(owner_id=user_id) if user_id else queryset.none()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        result_path = os.path.join(instance.output_folder or '', 'result.json')
        result_json = {}
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                result_json = json.load(f)
        data['result_json'] = result_json
        return Response(data)
