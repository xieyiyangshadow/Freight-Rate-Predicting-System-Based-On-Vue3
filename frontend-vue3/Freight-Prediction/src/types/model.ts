export interface ModelMetrics {
    r2_score: number
    mse: number
    rmse: number
    mae: number
}

export interface ModelMetricsFile {
    model_name: string
    dataset_name: string
    training_date: string
    training_duration: number
    metrics: ModelMetrics
    additional_info: {
        train_samples: number
        test_samples: number
        train_test_split_ratio: number
    }
}

export interface Model {
    model_id: string
    user_provided_name: string
    description: string
    owner_id: string
    dataset_id: string
    target_column: string
    training_status: 'pending' | 'training' | 'completed' | 'failed'
    create_time: string
    update_time: string
    metrics: ModelMetrics | null
}

export interface ModelUploadRequest {
    upload_mode: 'train' | 'ready'
    dataset_id: string
    evaluation_file: File
    model_file: File
    user_provided_name: string
    description: string
}

export interface ModelListResponse {
    message: string
    data: Model[]
}

export interface ModelUploadResponse {
    message: string
    data: Model
}

export interface ModelState {
    models: Model[]
    currentModel: Model | null
    isLoading: boolean
    error: string | null
}