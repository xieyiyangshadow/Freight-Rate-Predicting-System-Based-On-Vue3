from rest_framework import serializers
from .models import PredictionTask
from apps.model.models import Model
from apps.dataset.models import Dataset

class CreatePredictionTaskSerializer(serializers.Serializer):
    """ 
    创建预测任务的序列化器
    """
    task_name = serializers.CharField(max_length=255)
    task_description = serializers.CharField(allow_blank=True, required=False)
    dataset_id = serializers.UUIDField()
    model_ids = serializers.ListField(child=serializers.UUIDField())
    input_data = serializers.JSONField()
    
    def validate(self, data):
        """ 
        全局验证
        """
        dataset_id = data.get('dataset_id')
        model_ids = data.get('model_ids')
        
        # 验证数据集是否存在
        if not Dataset.objects.filter(dataset_id=dataset_id).exists():
            raise serializers.ValidationError("数据集不存在")
        
        # 验证模型是否存在
        models = Model.objects.filter(model_id__in=model_ids)
        if not model_ids:
            raise serializers.ValidationError("至少需要选择一个模型")
        for model_id in model_ids:
            if not Model.objects.filter(model_id=model_id).exists():
                raise serializers.ValidationError(f"模型 {model_id} 不可用")
        
        for model in models:
            if model.dataset_id != dataset_id:
                raise serializers.ValidationError(f"模型 {model.model_id} 不适用于选择的数据集")
            
        input_data = data.get('input_data')
        required_columns = Dataset.objects.get(dataset_id=dataset_id).columns - {Dataset.objects.get(dataset_id=dataset_id).target_column}
        input_columns = set(input_data.keys())
        if input_columns != required_columns:
            missing = required_columns - input_columns
            extra = input_columns - required_columns
            msg = ""
            if missing:
                msg += f"缺少输入列: {', '.join(missing)}. "
            if extra:
                msg += f"包含额外列: {', '.join(extra)}."
            raise serializers.ValidationError(msg)
        
        return data
    
class PredictionTaskSerializer(serializers.ModelSerializer):
    """ 
    预测任务序列化器
    """
    models_info = serializers.SerializerMethodField()
    
    class Meta:
        model = PredictionTask
        fields = [
            'task_id',
            'task_name',
            'task_description',
            'owner',
            'dataset',
            'input_data',
            'results',
            'create_time',
            'update_time',
            'status',
            'models_info'
        ]
        read_only_fields = [
            'results',
            'status'
        ]
        
    def get_models_info(self, obj):
        """
        获取模型的详细信息
        """
        return [
            {
                "model_id": str(model.model_id),
                "model_name": model.user_provided_name,
                "training_status": model.training_status
            }
            for model in obj.model.all()
        ]