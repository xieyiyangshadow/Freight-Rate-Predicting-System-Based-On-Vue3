from celery import shared_task
from .models import PredictionTask
from apps.model.models import Model
import pickle
import joblib
import pandas as pd
import json

@shared_task(bind=True)
def execute_prediction_task(self, task_id):
    """
    异步执行预测任务
    """
    try:
        task = PredictionTask.objects.get(task_id=task_id)
        
        task.status = 'running'
        task.save()
        
        models = task.model.all()
        
        input_df = pd.DataFrame([task.input_data])
        
        results = {}
        for model in models:
            try:
                if model.model_file_path.endswith('.joblib'):
                    loaded_model = joblib.load(model.model_file_path)
                else:
                    with open(model.model_file_path, 'rb') as f:
                        loaded_model = pickle.load(f)
                
                prediction = loaded_model.predict(input_df)
                
                results[model.user_provided_name] = float(prediction[0])
                
            except Exception as model_error:
                results[model.user_provided_name] = {
                    'error': str(model_error)
                }
        
        task.results = results
        task.status = 'completed'
        task.error_message = None  
        task.save()
        
        return {
            'status': 'success',
            'task_id': str(task_id),
            'message': '预测任务完成',
            'results': results
        }
        
    except PredictionTask.DoesNotExist:
        return {
            'status': 'failed',
            'task_id': str(task_id),
            'error': '预测任务不存在'
        }
    except Exception as e:
        try:
            task = PredictionTask.objects.get(task_id=task_id)
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
        except:
            pass
        
        return {
            'status': 'failed',
            'task_id': str(task_id),
            'error': str(e)
        }