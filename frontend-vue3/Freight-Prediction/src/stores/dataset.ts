import { defineStore } from "pinia"
import { ref, computed } from "vue"
import * as datasetApi from "@/api/dataset"
import type { Dataset, DatasetState, DatasetUploadRequest, DatasetListResponse, DatasetUploadResponse } from "@/types/dataset"

export const useDatasetStore  = defineStore('dataset', () => {
    const datasets = ref<Dataset[]>([])
    const currentDataset = ref<Dataset | null>(null)
    const isLoading = ref(false)
    const error = ref<string | null>(null)
    const currentDatasetDetail = ref<any | null>(null)

    const datasetCount = computed(() => (datasets.value || []).length)

    const uploadDataset = async (formData: FormData) => {
        isLoading.value = true
        error.value = null
        try {
            const response = await datasetApi.uploadDataset(formData)
            return response.data
        } catch (err: any) {
            error.value = err.response?.data?.detail || err.message || '数据集上传失败'
            throw err
        } finally {
            isLoading.value = false
        }
    }

    const fetchDatasets = async () => {
        isLoading.value = true
        error.value = null
        try {
            const response = await datasetApi.getDatasetList()
            datasets.value = response.data.datasets
            return response.data
        } catch (err: any) {
            error.value = err.response?.data?.detail || err.message || '列表获取失败'
            throw err
        } finally {
            isLoading.value = false
        }
    }

    const deleteDataset = async (datasetId: string) => {
        isLoading.value = true
        error.value = null
        try {
            const response = await datasetApi.deleteDataset(datasetId)
            datasets.value = datasets.value.filter(d => d.dataset_id !== datasetId)
            return response.data
        } catch (err: any) {
            error.value = err.response?.data?.detail || err.message || '数据集删除失败'
            throw err
        } finally {
            isLoading.value = false
        }
    }

    const fetchDatasetDetail = async (datasetId: string) => {
        isLoading.value = true
        error.value = null
        try {
            const response = await datasetApi.getDatasetDetail(datasetId)
            currentDatasetDetail.value = response.data
            return response.data
        } catch (err: any) {
            error.value = err.response?.data?.message || err.message || '获取数据集详情失败'
            throw err
        } finally {
            isLoading.value = false
        }
    }

    const setCurrentDataset = (dataset: Dataset | null) => {
        currentDataset.value = dataset
    }

    const clearError = () => {
        error.value = null
    }

    return {
        datasets,
        currentDataset,
        currentDatasetDetail,
        isLoading,
        error,
        datasetCount,
        uploadDataset,
        fetchDatasets,
        deleteDataset,
        fetchDatasetDetail,
        setCurrentDataset,
        clearError
    }
})