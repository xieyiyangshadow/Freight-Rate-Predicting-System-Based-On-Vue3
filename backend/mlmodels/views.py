from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import MLModel
from .serializers import MLModelSerializer
from django.utils import timezone
import os
import time
import joblib
from pathlib import Path
from django.contrib.auth import get_user_model
from freight.request_utils import extract_user_id
from freight.task_queue import enqueue_training
from .models import Dataset
from .serializers import DatasetSerializer
import csv
import json

class MLModelListCreateView(generics.ListCreateAPIView):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
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
            raise ValidationError({'detail': '请先登录后再上传模型'})

        # create DB record with uploading status
        # accept optional dataset and target_column
        request = serializer.context.get('request')
        dataset_id = None
        target_col = ''
        if request:
            dataset_id = request.data.get('dataset') or request.data.get('dataset_id')
            target_col = request.data.get('target_column', '')

        instance = serializer.save(owner=owner, status='uploading', dataset_id=dataset_id or None, target_column=target_col)
        base = os.path.join('models_storage', str(instance.id))
        os.makedirs(base, exist_ok=True)
        instance.file_path = os.path.join(base, 'model.pkl')
        instance.save()

        # if file uploaded in request, save it
        uploaded_file = None
        if request and hasattr(request, 'FILES'):
            uploaded_file = request.FILES.get('file')
        if uploaded_file:
            with open(instance.file_path, 'wb') as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)

        enqueue_training(instance.id, base)



class DatasetListCreateView(generics.ListCreateAPIView):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
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
            raise ValidationError({'detail': '请先登录后再上传数据集'})

        target_col = ''
        request = serializer.context.get('request')
        if request:
            target_col = request.data.get('target_column', '')

        instance = serializer.save(owner=owner, target_column=target_col)
        base = os.path.join('datasets_storage', str(instance.id))
        os.makedirs(base, exist_ok=True)
        instance.file_path = os.path.join(base, 'dataset.csv')
        instance.save()

        request = serializer.context.get('request')
        uploaded_file = None
        if request and hasattr(request, 'FILES'):
            uploaded_file = request.FILES.get('file')
        if uploaded_file:
            with open(instance.file_path, 'wb') as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)
            # try to read header and extract columns
            try:
                with open(instance.file_path, 'r', encoding='utf-8') as handle:
                    reader = csv.reader(handle)
                    header = next(reader, [])
                instance.columns = json.dumps(header)
                instance.save(update_fields=['file_path', 'columns'])
            except Exception:
                instance.columns = json.dumps([])
                instance.save(update_fields=['file_path', 'columns'])


class DatasetDetailView(generics.RetrieveUpdateAPIView):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    authentication_classes = []
    permission_classes = [__import__('rest_framework.permissions', fromlist=['AllowAny']).AllowAny]

    def get_queryset(self):
        user_id = extract_user_id(self.request)
        queryset = super().get_queryset()
        return queryset.filter(owner_id=user_id) if user_id else queryset.none()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        # return parsed columns as list
        try:
            cols = json.loads(instance.columns) if instance.columns else []
        except Exception:
            cols = []
        data['columns_list'] = cols
        
        # read CSV data preview (first 10 rows)
        data_preview = []
        if instance.file_path and os.path.exists(instance.file_path):
            try:
                with open(instance.file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader):
                        if i >= 10:  # Only read first 10 rows
                            break
                        data_preview.append(row)
            except Exception:
                pass
        
        data['data_preview'] = data_preview
        data['total_rows'] = self._count_csv_rows(instance.file_path)
        return Response(data)
    
    def _count_csv_rows(self, file_path):
        """Count total rows in CSV file"""
        if not file_path or not os.path.exists(file_path):
            return 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f) - 1  # -1 for header
        except Exception:
            return 0

class MLModelDetailView(generics.RetrieveAPIView):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    authentication_classes = []
    permission_classes = [__import__('rest_framework.permissions', fromlist=['AllowAny']).AllowAny]

    def get_queryset(self):
        user_id = extract_user_id(self.request)
        queryset = super().get_queryset()
        return queryset.filter(owner_id=user_id) if user_id else queryset.none()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        data = self.get_serializer(instance).data
        metrics_text = ''
        if instance.metrics_path and os.path.exists(instance.metrics_path):
            with open(instance.metrics_path, 'r', encoding='utf-8') as f:
                metrics_text = f.read()
        file_size_bytes = Path(instance.file_path).stat().st_size if instance.file_path and os.path.exists(instance.file_path) else 0
        data['metrics_text'] = metrics_text
        data['file_size_bytes'] = file_size_bytes
        return Response(data)
