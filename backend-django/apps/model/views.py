from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Model
from .Serializer import ModelSerializer, ModelUploadSerializer
from apps.dataset.models import Dataset
import uuid
import os
import pickle
import json
import pandas as pd
from datetime import datetime
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error, precision_score, recall_score, f1_score, r2_score
import numpy as np

# Create your views here.
class ModelUploadView(APIView):
    """ 
    模型上传视图
    POST /api/model/upload/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """ 
        处理模型上传
        请求体:
        {
            "upload_mode": "train" 或 "ready",
            "dataset_id": "关联的数据集ID",
            "evaluation_file": "评估指标文件，JSON格式",当upload_mode为ready时必填
            "model_file": "上传的模型文件，支持pickle或joblib格式",
            "user_provided_name": "用户提供的模型名称",
            "description": "模型描述"
        }
        """
        serializer = ModelUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_provided_name = serializer.validated_data['user_provided_name']
            description = serializer.validated_data.get('description', '')
            dataset_id = serializer.validated_data['dataset_id']
            model_file = serializer.validated_data['model_file']
            upload_mode = serializer.validated_data['upload_mode']
            
            models_dir = os.path.join('models')
            if not os.path.exists(models_dir):
                os.makedirs(models_dir)
            model_filename = f"{uuid.uuid4()}_{datetime.now().timestamp()}"
            model_extension = '.joblib' if model_file.name.endswith('.joblib') else '.pkl'
            model_file_path = os.path.join(models_dir, f"{model_filename}{model_extension}")
            
            with open(model_file_path, 'wb+') as destination:
                for chunk in model_file.chunks():
                    destination.write(chunk)
                    
            # 直接上传模型
            if upload_mode == 'ready':
                evaluation_file = serializer.validated_data.get('evaluation_file')
                evaluation_file_path = os.path.join(models_dir, f"{model_filename}_evaluation.json")
                with open(evaluation_file_path, 'wb+') as destination:
                    for chunk in evaluation_file.chunks():
                        destination.write(chunk)
                
                model = Model.objects.create(
                    model_id=uuid.uuid4(),
                    user_provided_name=user_provided_name,
                    description=description,
                    owner=request.user,
                    dataset=Dataset.objects.get(dataset_id=dataset_id),
                    model_file_path=model_file_path,
                    evaluation_file_path=evaluation_file_path,
                    training_status='completed',
                    create_time=datetime.now(),
                    update_time=datetime.now()
                )
                
                response_serializer = ModelSerializer(model)
                return Response(
                    {
                        'message': '模型上传成功',
                        'model': response_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
                
            # 需要训练的模型
            else:
                model = Model.objects.create(
                    model_id=uuid.uuid4(),
                    user_provided_name=user_provided_name,
                    description=description,
                    owner=request.user,
                    dataset=Dataset.objects.get(dataset_id=dataset_id),
                    model_file_path=model_file_path,
                    training_status='pending',
                    create_time=datetime.now(),
                    update_time=datetime.now()
                )
                
                response_serializer = ModelSerializer(model)
                
                try:
                    model.training_status = 'training'
                    model.save()
                    
                    df = pd.read_csv(model.dataset.file_path)
                    target_column = model.dataset.target_column
                    X = df.drop(columns=[target_column])
                    y = df[target_column]
                    
                    train_X, val_X, train_y, val_y = train_test_split(X, y, test_size=0.2, random_state=42)
                    
                    if model_extension == '.joblib':
                        clf = joblib.load(model_file_path)
                    else:
                        with open(model_file_path, 'rb') as f:
                            clf = pickle.load(f)
                    
                    clf.fit(train_X, train_y)
                    y_pred = clf.predict(val_X)
                    r2 = r2_score(val_y, y_pred)
                    mse = mean_squared_error(val_y, y_pred)
                    rmse = np.sqrt(mse)
                    mae = mean_absolute_error(val_y, y_pred)
                    
                    metrics = {
                        "model_name": user_provided_name,
                        "dataset_name": model.dataset.user_provided_name,
                        "training_date": datetime.now().isoformat(),
                        "training_duration": (datetime.now() - model.create_time).total_seconds(),
                        "metrics": {
                            "r2_score": r2,
                            "mean_squared_error": mse,
                            "root_mean_squared_error": rmse,
                            "mean_absolute_error": mae
                        },
                        "additional_info": {
                            "train_samples": len(train_X),
                            "val_samples": len(val_X),
                            "train_test_split_ratio": 0.2
                        }
                    }
                    
                    if model_extension == '.joblib':
                        joblib.dump(clf, model_file_path)
                    else:
                        with open(model_file_path, 'wb') as f:
                            pickle.dump(clf, f)
                            
                    evaluation_file_path = os.path.join(models_dir, f"{model_filename}_evaluation.json")
                    with open(evaluation_file_path, 'w', encoding='utf-8') as f:
                        json.dump(metrics, f, ensure_ascii=False, indent=4)
                        
                    model.evaluation_file_path = evaluation_file_path
                    model.training_status = 'completed'
                    model.save()
                
                except Exception as e:
                    model.training_status = 'failed'
                    model.save()
                    return Response(
                        {
                            'message': f'模型训练失败: {str(e)}',
                            'model': response_serializer.data
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                response_serializer = ModelSerializer(model)
                return Response(
                    {
                        'message': '模型上传并训练成功',
                        'model': response_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            
        except Exception as e:
            return Response(
                {
                    'message': f'模型上传失败: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ModelListView(APIView):
    """ 
    模型列表视图
    GET /api/model/list/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """ 
        获取用户的模型列表
        """
        models = Model.objects.filter(owner=request.user)
        serializer = ModelSerializer(models, many=True)
        return Response(
            {
                'message': '模型列表获取成功',
                'models': serializer.data
            },
            status=status.HTTP_200_OK
        )

class ModelDeleteView(APIView):
    """ 
    模型删除视图
    DELETE /api/model/delete/{model_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, model_id):
        """ 
        删除指定ID的模型
        DELETE /api/model/delete/{model_id}/
        """
        try:
            model = Model.objects.get(model_id=model_id, owner=request.user)
            if os.path.exists(model.model_file_path):
                os.remove(model.model_file_path)
                
            if model.evaluation_file_path and os.path.exists(model.evaluation_file_path):
                os.remove(model.evaluation_file_path)
            
            model.delete()
            
            return Response(
                {
                    "message": "模型删除成功"
                },
                status=status.HTTP_200_OK
            )
        except Model.DoesNotExist:
            return Response(
                {
                    "message": "模型不存在或没有权限删除"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    "message": f"模型删除失败: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )