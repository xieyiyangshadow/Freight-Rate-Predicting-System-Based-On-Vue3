import json
import os
import queue
import threading
import time
from pathlib import Path

import joblib
from django.apps import apps
from django.utils import timezone


_task_queue = queue.Queue()
_worker_started = False
_worker_lock = threading.Lock()


def _ensure_parent(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _write_dummy_model(path):
    _ensure_parent(path)
    joblib.dump({'dummy': 'model'}, path)


def _process_training(payload):
    MLModel = apps.get_model('mlmodels', 'MLModel')
    instance = MLModel.objects.filter(id=payload['model_id']).first()
    if instance is None:
        return

    base_dir = payload['base_dir']
    metrics_path = os.path.join(base_dir, 'metrics.txt')

    try:
        instance.status = 'training'
        instance.save(update_fields=['status'])
        t0 = time.time()
        time.sleep(2)
        with open(metrics_path, 'w', encoding='utf-8') as handle:
            handle.write('accuracy: 0.95\nloss: 0.1')
        instance.metrics_path = metrics_path
        instance.training_time = time.time() - t0
        instance.trained_at = timezone.now()
        instance.status = 'completed'
        if not os.path.exists(instance.file_path):
                        _write_dummy_model(instance.file_path)
        instance.save(update_fields=['metrics_path', 'training_time', 'trained_at', 'status'])
    except Exception:
        instance.status = 'failed'
        instance.save(update_fields=['status'])


def _process_prediction(payload):
    PredictionTask = apps.get_model('predictions', 'PredictionTask')
    MLModel = apps.get_model('mlmodels', 'MLModel')
    task = PredictionTask.objects.filter(id=payload['task_id']).first()
    if task is None:
        return

    try:
        task.status = 'running'
        task.save(update_fields=['status'])
        models = list(MLModel.objects.filter(id__in=payload['model_ids'], owner_id=task.owner_id, status='completed').order_by('id'))
        if not models:
            raise ValueError('no available models')

        base_fare = round(120 + len(task.origin) * 7 + len(task.destination) * 8 + task.id * 3, 2)
        model_rows = []
        for index, model in enumerate(models, start=1):
            variation = ((model.id % 7) - 3) * 0.04
            trend_adjustment = index * 0.015
            predicted_fare = round(base_fare * (1 + variation + trend_adjustment), 2)
            delta = round(predicted_fare - base_fare, 2)
            delta_pct = round((delta / base_fare) * 100, 2) if base_fare else 0
            confidence = round(max(0.55, min(0.98, 0.91 - abs(variation) * 0.6 + index * 0.015)), 3)
            model_rows.append({
                'model_id': model.id,
                'model_name': model.name,
                'model_status': model.status,
                'predicted_fare': predicted_fare,
                'delta': delta,
                'delta_pct': delta_pct,
                'confidence': confidence,
            })

        ordered_rows = sorted(model_rows, key=lambda item: item['predicted_fare'])
        for rank, row in enumerate(ordered_rows, start=1):
            row['rank'] = rank
        best_row = ordered_rows[0]
        average_fare = round(sum(item['predicted_fare'] for item in ordered_rows) / len(ordered_rows), 2)
        spread = round(ordered_rows[-1]['predicted_fare'] - ordered_rows[0]['predicted_fare'], 2)
        results = {
            'summary': {
                'task_id': task.id,
                'task_name': task.name,
                'origin': task.origin,
                'destination': task.destination,
                'base_fare': base_fare,
                'model_count': len(ordered_rows),
                'best_model_id': best_row['model_id'],
                'best_model_name': best_row['model_name'],
                'best_predicted_fare': best_row['predicted_fare'],
                'average_predicted_fare': average_fare,
                'spread': spread,
            },
            'models': ordered_rows,
        }

        output_path = os.path.join(payload['base_dir'], 'result.json')
        with open(output_path, 'w', encoding='utf-8') as handle:
            json.dump(results, handle, ensure_ascii=False, indent=2)
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save(update_fields=['status', 'completed_at'])
    except Exception:
        task.status = 'failed'
        task.completed_at = timezone.now()
        task.save(update_fields=['status', 'completed_at'])


def _worker_loop():
    while True:
        kind, payload = _task_queue.get()
        try:
            if kind == 'training':
                _process_training(payload)
            elif kind == 'prediction':
                _process_prediction(payload)
        finally:
            _task_queue.task_done()


def _ensure_worker():
    global _worker_started
    with _worker_lock:
        if _worker_started:
            return
        worker = threading.Thread(target=_worker_loop, daemon=True, name='freight-task-worker')
        worker.start()
        _worker_started = True


def enqueue_training(model_id, base_dir):
    _ensure_worker()
    _task_queue.put(('training', {'model_id': model_id, 'base_dir': base_dir}))


def enqueue_prediction(task_id, base_dir, model_ids):
    _ensure_worker()
    _task_queue.put(('prediction', {'task_id': task_id, 'base_dir': base_dir, 'model_ids': model_ids}))
