from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PredictionTask
from .Serializer import CreatePredictionTaskSerializer, PredictionTaskSerializer
from .tasks import execute_prediction_task
from apps.model.models import Model
from apps.dataset.models import Dataset
import uuid

# Create your views here.
class CreatePredictionTaskView(APIView):
    """ 
    创建预测任务视图
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """ 
        POST /api/prediction/tasks/
        请求体：
        {
            "task_name": "任务名称",
            "task_description": "任务描述",
            "dataset_id": "关联的数据集ID",
            "model_ids": ["关联的模型ID列表"],
            "input_data": {"输入数据的JSON格式"}
        }
        """
        serializer = CreatePredictionTaskSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validated_data = serializer.validated_data
            
            task = PredictionTask.objects.create(
                task_id=uuid.uuid4(),
                task_name=validated_data['task_name'],
                task_description=validated_data.get('task_description', ''),
                owner=request.user,
                dataset_id=validated_data['dataset_id'],
                input_data=validated_data['input_data'],
                status='pending'
            )
            
            model_ids = validated_data['model_ids']
            models = Model.objects.filter(model_id__in=model_ids)
            task.model.set(models)
            
            execute_prediction_task.delay(str(task.task_id))
            task_serializer = PredictionTaskSerializer(task)
            return Response(
                {
                 'message': '预测任务已创建并正在执行',
                 'task': task_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {
                    'message': f'创建预测任务失败, 错误: {str(e)}',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PredictionTaskListView(APIView):
    """ 
    获取用户的预测任务列表视图
    GET /api/prediction/tasks/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tasks = PredictionTask.objects.filter(owner=request.user)
        serializer = PredictionTaskSerializer(tasks, many=True)
        return Response(
            {
                'message': '获取预测任务列表成功',
                'tasks': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
class PredictionTaskDetailView(APIView):
    """ 
    获取预测任务详情视图
    GET /api/prediction/tasks/{task_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, task_id):
        try:
            task = PredictionTask.objects.get(
                task_id=task_id, 
                owner=request.user
            )
            serializer = PredictionTaskSerializer(task)
            return Response(
                {
                    'message': '获取预测任务详情成功',
                    'task': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except PredictionTask.DoesNotExist:
            return Response(
                {
                    'message': '预测任务不存在或没有权限访问'
                },
                status=status.HTTP_404_NOT_FOUND
            )