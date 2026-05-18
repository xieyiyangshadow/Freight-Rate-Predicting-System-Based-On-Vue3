export interface PredictionTask {
    task_id: string
    task_name: string
    task_description: string
    status: 'pending' | 'running' | 'completed' | 'failed'
    dataset: string
    models_info: {
        model_id: string
        user_provided_name: string
        training_status: string
    }[]
    input_data: Record<string, any>
    results: Record<string, number | { error: string }> | null
    create_time: string
    update_time: string
}

export interface CreatePredictionRequest {
    task_name: string
    task_description?: string
    dataset_id: string
    model_ids: string[]
    input_data: Record<string, any>
}

export interface PredictionResponse {
    task: PredictionTask
}