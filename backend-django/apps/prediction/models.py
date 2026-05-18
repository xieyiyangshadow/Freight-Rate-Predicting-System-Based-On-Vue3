from django.db import models
from django.contrib.auth.models import User
from apps.model.models import Model
from apps.dataset.models import Dataset
import uuid
import json

# Create your models here.
class PredictionTask(models.Model):
    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_name = models.CharField(max_length=255)
    task_description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    model = models.ManyToManyField(Model)
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, null=True, blank=True) #不联级删除，因为数据集删除了，预测任务也不一定要删除
    input_data = models.JSONField()
    results = models.JSONField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = [
        ('pending', '待预测'),
        ('running', '预测中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    
    class Meta:
        ordering = ['-create_time']
        