from celery import shared_task
from .models import Model
from apps.dataset.models import Dataset
import os
import pickle
import json
import pandas as pd
from django.utils import timezone
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import numpy as np
from sklearn.impute import SimpleImputer
from catboost import CatBoostRegressor, CatBoostClassifier
from lightgbm import LGBMRegressor, LGBMClassifier
from xgboost import XGBRegressor, XGBClassifier

@shared_task(bind=True)
def train_model_task(self, model_id):
    """ 
    异步模型训练任务
    """
    try:
        model = Model.objects.get(model_id=model_id)
        dataset = model.dataset
        model.training_status = 'training'
        model.save()
        
        df = pd.read_csv(dataset.file_path)
        target_column = dataset.target_column
        X = df.drop(columns=[target_column])
        categorical_columns = X.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_columns:
            X = pd.get_dummies(X, columns=categorical_columns, drop_first=True)
        y = df[target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # 处理缺失值：使用均值填充数值特征，防止 LinearRegression 等不接受 NaN 的模型出错
        imputer = SimpleImputer(strategy='mean')
        X_train_imputed = pd.DataFrame(imputer.fit_transform(X_train), columns=X_train.columns, index=X_train.index)
        X_test_imputed = pd.DataFrame(imputer.transform(X_test), columns=X_test.columns, index=X_test.index)
        
        model_extension = '.joblib' if model.model_file_path.endswith('.joblib') else '.pkl'
        
        if model_extension == '.joblib':
            user_model = joblib.load(model.model_file_path)
        else:
            with open(model.model_file_path, 'rb') as f:
                user_model = pickle.load(f)
        # 用填充后的数据训练并评估
        user_model.fit(X_train_imputed, y_train)
        y_pred = user_model.predict(X_test_imputed)
        
        r2 = r2_score(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        
        training_columns = X_train_imputed.columns.tolist()

        metrics = {
            "model_name": model.user_provided_name,
            "dataset_name": dataset.user_provided_name,
            "training_date": timezone.now().isoformat(),
            "training_duration": (timezone.now() - model.create_time).total_seconds(),
            "metrics": {
                "r2_score": float(r2),
                "mse": float(mse),
                "rmse": float(rmse),
                "mae": float(mae)
            },
            "additional_info": {
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "train_test_split_ratio": 0.2
            }
        }
        
        if model_extension == '.joblib':
            joblib.dump(user_model, model.model_file_path)
        else:
            with open(model.model_file_path, 'wb') as f:
                pickle.dump(user_model, f)

        # 将预处理器也保存为 joblib，供预测时重用
        preprocessor_file_path = os.path.dirname(model.model_file_path) + f"/{model.model_id}_preprocessor.joblib"
        try:
            joblib.dump(imputer, preprocessor_file_path)
        except Exception:
            preprocessor_file_path = None
        
        # 把训练时使用的列也写入 evaluation 文件，供预测时对齐输入使用
        metrics['training_columns'] = training_columns
        metrics['categorical_columns'] = categorical_columns
        metrics['preprocessor_file_path'] = preprocessor_file_path

        evaluation_file_path = os.path.dirname(model.model_file_path) + f"/{model.model_id}_evaluation.json"
        with open(evaluation_file_path, 'w') as f:
            json.dump(metrics, f, indent=4)
            
        model.evaluation_file_path = evaluation_file_path
        model.training_status = 'completed'
        model.save()
        
        return {
            "status": "success",
            "model_id": str(model.model_id),
            "message": "模型训练完成",
        }
    except Exception as e:
        model = Model.objects.get(model_id=model_id)
        model.training_status = 'failed'
        model.save()
        
        return {
            "status": "failed",
            "model_id": str(model.model_id),
            "error": str(e)
        }