from rest_framework import serializers
from .models import PredictionTask

class PredictionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionTask
        fields = ('id','owner','name','origin','destination','models_used','status','output_folder','created_at','completed_at')
        read_only_fields = ('owner', 'status', 'output_folder', 'created_at', 'completed_at')
