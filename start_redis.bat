cd backend-django
./.venv/Scripts/Activate.ps1
redis-server
celery -A config worker -l info --pool=solo