from django.db import models
from django.conf import settings

class PredictionTask(models.Model):
    STATUS_CHOICES = [
        ('pending','待处理'),
        ('running','运行中'),
        ('completed','已完成'),
        ('failed','失败'),
    ]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    origin = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    models_used = models.ManyToManyField('mlmodels.MLModel')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    output_folder = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Task {self.id} - {self.name} ({self.status})"
