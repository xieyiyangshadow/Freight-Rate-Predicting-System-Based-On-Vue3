from rest_framework import serializers
from .models import Model
from apps.dataset.models import Dataset
import json

class ModelSerializer(serializers.ModelSerializer):
    """ 
    模型序列化器
    """
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    dataset_name = serializers.CharField(source='dataset.user_provided_name', read_only=True)
    target_column = serializers.CharField(source='dataset.target_column', read_only=True)
    
    metrics = serializers.SerializerMethodField()
    
    class Meta:
        model = Model
        fields = [
            'model_id', 'user_provided_name', 'description',
            'owner_id', 'dataset_name', 'target_column',
            'training_status', 'create_time', 'update_time',
            'metrics'
        ]
        read_only_fields = [
            'model_id', 'create_time', 'update_time',
            'owner_id', 'metrics'
        ]
        
    def get_metrics(self, obj):
        """ 
        读取Json格式的评估指标文件并返回
        """
        if not obj.evaluation_file_path:
            return None
        
        try:
            with open(obj.evaluation_file_path, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            return metrics
        except Exception as e:
            return {"error": f"无法读取评估指标文件: {str(e)}"}
        
class ModelUploadSerializer(serializers.Serializer):
    """ 
    模型上传序列化器
    """
    user_provided_name = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)
    dataset_id = serializers.UUIDField()
    model_file = serializers.FileField()
    
    upload_mode = serializers.ChoiceField(
        choices=['train', 'ready'],
        default='train'
    )
    
    evaluation_file = serializers.FileField(required=False)
    
    def validate_model_file(self, value):
        """ 
        验证模型文件类型
        """
        if not value.name.endswith('.pkl') and not value.name.endswith('.joblib'):
            raise serializers.ValidationError("模型文件必须是.pkl或.joblib格式")
        return value
    
    def validate_evaluation_file(self, value):
        """ 
        验证评估指标文件格式
        """
        if value:
            if not value.name.endswith('.json'):
                raise serializers.ValidationError("评估指标文件必须是.json格式")
            
            try:
                content = value.read()
                json.loads(content)
                value.seek(0)
            except json.JSONDecodeError:
                raise serializers.ValidationError("评估指标文件必须是有效的JSON格式")
        return value
    
    def validate(self, data):
        """ 
        整体验证
        """
        upload_mode = data.get('upload_mode')
        dataset_id = data.get('dataset_id')
        
        try:
            dataset = Dataset.objects.get(dataset_id=dataset_id)
            data['dataset'] = dataset
        except Dataset.DoesNotExist:
            raise serializers.ValidationError("关联的数据集不存在")
        
        if upload_mode == 'ready' and not data.get('evaluation_file'):
            raise serializers.ValidationError("当上传模式为'ready'时，评估指标文件是必需的")
        
        return data