from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .Serializer import DatasetSerializer, DatasetUploadSerializer
from .models import Dataset
from django.contrib.auth.models import User
import uuid
from datetime import datetime
import os
import pandas as pd

# Create your views here.

class DatasetUploadView(APIView):
    """ 
    数据集上传视图
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """ 
        POST /api/dataset/upload/
        请求体：
        {
            "user_id": "上传数据集的用户ID",
            "user_provided_name": "用户提供的数据集名称",
            "description": "数据集描述",
            "file": "上传的数据集文件，支持CSV格式",
            "target_column": "预测目标列名称"
        }
        """
        serializer = DatasetUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        sys_name = f"{uuid.uuid4()}_{datetime.now().timestamp()}"
        
        create_time = datetime.now()
        owner = request.data.get('user_id')
        file = request.FILES.get('file')
        file = pd.read_csv(file)
        file.to_csv(f"datasets/{sys_name}.csv", index=False)
        file_path = f"datasets/{sys_name}.csv"
        columns = list(file.columns)
        target_column = serializer.validated_data.get('target_column')
        description = serializer.validated_data.get('description', '')
        user_provided_name = serializer.validated_data.get('user_provided_name')
        
        data_types = {}
        for col in columns:
            if pd.api.types.is_numeric_dtype(file[col]):
                data_types[col] = 'numeric'
            elif pd.api.types.is_string_dtype(file[col]):
                data_types[col] = 'categorical'
            else:
                data_types[col] = 'other'
        
        dataset = Dataset.objects.create(
            dataset_id=uuid.uuid4(),
            user_provided_name=user_provided_name,
            description=description,
            sys_name=sys_name,
            create_time=create_time,
            owner=User.objects.get(id=owner),
            file_path=file_path,
            columns=columns,
            target_column=target_column,
            data_types=data_types
        )
        
        response_serializer = DatasetSerializer(dataset)
        return Response(
            {
                "message": "数据集上传成功",
                "dataset": response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
        
class DatasetListView(APIView):
    """ 
    数据集列表视图
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """ 
        GET /api/dataset/list/
        请求参数：
        {
            "user_id": "查询数据集的用户ID"
        }
        """
        user_id = request.query_params.get('user_id')
        datasets = Dataset.objects.filter(owner__id=user_id)
        serializer = DatasetSerializer(datasets, many=True)
        return Response(
            {
                "message": "数据集列表获取成功",
                "datasets": serializer.data
            },
            status=status.HTTP_200_OK
        )
        