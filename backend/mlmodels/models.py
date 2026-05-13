from django.db import models
from django.conf import settings

class MLModel(models.Model):
    STATUS_CHOICES = [
        ('uploading','上传中'),
        ('training','正在训练'),
        ('completed','训练完成'),
        ('failed','训练失败'),
    ]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500, blank=True)
    metrics_path = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    created_at = models.DateTimeField(auto_now_add=True)
    trained_at = models.DateTimeField(null=True, blank=True)
    training_time = models.FloatField(null=True, blank=True)
    dataset = models.ForeignKey('Dataset', null=True, blank=True, on_delete=models.SET_NULL)
    target_column = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.id} - {self.name} ({self.status})"


class Dataset(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500, blank=True)
    columns = models.TextField(blank=True)  # JSON list of column names
    target_column = models.CharField(max_length=200, blank=True)  # Selected target column
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.name}"
