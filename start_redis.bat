cd backend-django
./.venv/Scripts/Activate.ps1
redis-server redis.conf
celery -A config worker -l info --pool=solo