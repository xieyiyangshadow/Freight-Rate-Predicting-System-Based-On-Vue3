import os
from celery import Celery

# 设置默认 Django 配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# 从 Django 配置中读取 Celery 配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有应用中的 tasks.py
app.autodiscover_tasks()