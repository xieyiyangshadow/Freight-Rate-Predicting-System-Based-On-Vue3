from celery import shared_task
import os
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
                # 为预测输入应用与训练相同的数据预处理：
                # 读取训练使用的数据集，识别其中的分类列并对这些列进行 one-hot 编码，
                # 然后将输入行编码并重建与训练时相同的列顺序/缺失列填 0。
                try:
                    # 优先从 evaluation 文件读取训练时保存的列信息
                    training_columns = None
                    categorical_columns = None
                    preprocessor_file_path = None
                    if model.evaluation_file_path and os.path.exists(model.evaluation_file_path):
                        try:
                            with open(model.evaluation_file_path, 'r', encoding='utf-8') as ef:
                                eval_json = json.load(ef)
                                training_columns = eval_json.get('training_columns')
                                categorical_columns = eval_json.get('categorical_columns')
                                preprocessor_file_path = eval_json.get('preprocessor_file_path')
                        except Exception:
                            training_columns = None

                    dataset = model.dataset
                    df_full = pd.read_csv(dataset.file_path)
                    target_col = dataset.target_column
                    X_full = df_full.drop(columns=[target_col])

                    # 如果 evaluation 中没有列信息，则根据原始数据推断
                    if training_columns is None:
                        categorical_columns = X_full.select_dtypes(include=['object', 'category']).columns.tolist()
                        if categorical_columns:
                            X_full_encoded = pd.get_dummies(X_full, columns=categorical_columns, drop_first=True)
                        else:
                            X_full_encoded = X_full
                        training_columns = X_full_encoded.columns.tolist()

                    # 对输入进行相同的编码（若已知 categorical_columns，则使用之）
                    input_proc = input_df.copy()
                    if categorical_columns:
                        input_proc = pd.get_dummies(input_proc, columns=categorical_columns, drop_first=True)

                    # 对齐列，缺失列补 0，多余列则按训练列截取
                    input_proc = input_proc.reindex(columns=training_columns, fill_value=0)

                    # 若训练时保存了预处理器（如 SimpleImputer），优先使用之
                    used_preprocessor = False
                    if preprocessor_file_path and os.path.exists(preprocessor_file_path):
                        try:
                            preprocessor = joblib.load(preprocessor_file_path)
                            input_proc = pd.DataFrame(preprocessor.transform(input_proc), columns=input_proc.columns, index=input_proc.index)
                            used_preprocessor = True
                        except Exception:
                            used_preprocessor = False

                    # 回退策略：强制将所有列转为数值，无法转换的置为 NaN 后填 0，避免字符串传入模型导致异常
                    if not used_preprocessor:
                        for col in input_proc.columns:
                            input_proc[col] = pd.to_numeric(input_proc[col], errors='coerce')
                        input_proc = input_proc.fillna(0)

                    prediction = loaded_model.predict(input_proc)
                    results[model.user_provided_name] = float(prediction[0])
                except Exception as prep_err:
                    results[model.user_provided_name] = {'error': f'预测前处理失败: {str(prep_err)}'}
                
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