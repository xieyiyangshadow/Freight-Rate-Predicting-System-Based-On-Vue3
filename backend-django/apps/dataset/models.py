from django.db import models
from django.contrib.auth.models import User
import uuid
import os
from datetime import datetime

# Create your models here.

class Dataset(models.Model):
    dataset_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_provided_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sys_name = models.CharField(max_length=255, unique=True)
    create_time = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)
    columns = models.JSONField()
    target_column = models.CharField(max_length=255, blank=True)
    data_types = models.JSONField()
    
    class Meta:
        ordering = ['-create_time']
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'
        
    def __str__(self):
        return f"{self.user_provided_name} ({self.dataset_id}) - {self.owner.username}"