from rest_framework import serializers
from .models import MLModel, Dataset
import json


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ('id', 'owner', 'name', 'file_path', 'columns', 'target_column', 'uploaded_at')
        read_only_fields = ('owner', 'file_path', 'columns', 'uploaded_at')


class MLModelSerializer(serializers.ModelSerializer):
    dataset = serializers.PrimaryKeyRelatedField(queryset=Dataset.objects.all(), allow_null=True, required=False)

    class Meta:
        model = MLModel
        fields = ('id','owner','name','file_path','metrics_path','status','created_at','trained_at','training_time','dataset','target_column')
        read_only_fields = ('owner', 'file_path', 'metrics_path', 'status', 'created_at', 'trained_at', 'training_time')
