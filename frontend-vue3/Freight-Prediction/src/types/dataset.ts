export interface DatasetUploadRequest {
    user_provided_name: string
    description: string
    file: File
    target_column: string
}

export interface Dataset {
    dataset_id: string
    user_provided_name: string
    description: string
    sys_name: string
    create_time: string
    owner_id: string
    file_path: string
    columns: string[]
    target_column: string
    data_types: Record<string, boolean>
}

export interface DatasetListResponse {
    message: string
    datasets: Dataset[]
}

export interface DatasetUploadResponse {
    message: string
    dataset: Dataset
}

export interface DatasetDetailResponse {
    message: string
    dataset: Dataset
    preview: Array<Record<string, string | number | null>>
    describe: Record<string, Record<string, number | null>>
    histograms: Record<string, { counts: number[]; bin_edges: number[] }>
    correlation: Record<string, Record<string, number>>
}

export interface DatasetState {
    datasets: Dataset[]
    currentDataset: Dataset | null
    isLoading: boolean
    error: string | null
}
