from rest_framework import serializers
from .models import Dataset
import pandas as pd
import uuid
from datetime import datetime
import os

class DatasetSerializer(serializers.ModelSerializer):
    """ 
    数据集序列化器
    """
    owner_id = serializers.CharField(source='owner.id', read_only=True)
    
    class Meta:
        model = Dataset
        fields = ['dataset_id', 'user_provided_name', 'description', 'sys_name', 'create_time', 'owner_id', 'file_path', 'columns', 'target_column', 'data_types']
        read_only_fields = ['dataset_id', 'create_time', 'owner_id']
        
class DatasetUploadSerializer(serializers.Serializer):
    """ 
    数据集上传序列化器
    """
    user_provided_name = serializers.CharField(max_length=255, required=True, help_text="用户提供的数据集名称")
    description = serializers.CharField(required=False, allow_blank=True, help_text="数据集描述")
    file = serializers.FileField(required=True, help_text="上传的数据集文件，支持CSV格式")
    target_column = serializers.CharField(max_length=255, required=True, help_text="预测目标列名称")
    
    def validate_file(self,value):
        """ 
        验证上传的文件是否为CSV格式
        """
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("只支持CSV格式的文件")
        return value
    
    def validate_target_column(self, value):
        """ 
        验证目标列是否存在于上传的CSV文件中,并且目标列名称不能为空
        """
        file = self.initial_data.get('file')
        if file:
            try:
                df = pd.read_csv(file)
                if not value or value.strip() == "":
                    raise serializers.ValidationError("目标列名称不能为空")
                if value not in df.columns:
                    raise serializers.ValidationError(f"目标列 '{value}' 不存在于上传的CSV文件中")
            except Exception as e:
                raise serializers.ValidationError(f"无法读取上传的CSV文件: {str(e)}")
        return value
    
    def validate(self,data):
        """ 
        验证 CSV 文件内容和目标列
        """
        file  = data.get('file')
        target_column = data.get('target_column')
        
        try:
            df = pd.read_csv(file)
            if df.isnull().values.any() or '' in df.columns:
                raise serializers.ValidationError("CSV文件中存在空值或空列，请确保数据完整")
            if target_column not in df.columns:
                raise serializers.ValidationError(f"目标列 '{target_column}' 不存在于上传的CSV文件中")
            data['dataframe'] = df
            data['columns'] = df.columns.tolist()
        except Exception as e:
            raise serializers.ValidationError(f"无法读取上传的CSV文件: {str(e)}")
        return data