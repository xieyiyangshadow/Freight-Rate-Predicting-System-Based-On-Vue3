from django.db import models
from django.contrib.auth.models import User
import uuid
from apps.dataset.models import Dataset

# Create your models here.

class Model(models.Model):
    STATUS_CHOICES = [
        ('pending', '待训练'),
        ('training', '训练中'),
        ('completed', '已完成'), #训练完成以及本地训练完成直接上传的模型
        ('failed', '训练失败')
    ]
    
    model_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_provided_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    model_file_path = models.CharField(max_length=255)
    evaluation_file_path = models.CharField(max_length=255, blank=True)
    
    training_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-create_time']
        verbose_name = '模型'
        verbose_name_plural = '模型'
        
    def __str__(self):
        return f"{self.user_provided_name} ({self.model_id}) - {self.owner.username}"