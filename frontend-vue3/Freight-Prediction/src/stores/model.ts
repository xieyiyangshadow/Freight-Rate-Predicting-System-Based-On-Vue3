import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as modelApi from '@/api/model'
import type { Model } from '@/types/model'

export const useModelStore = defineStore('model', () => {
    const models = ref<Model[]>([])
    const currentModel = ref<Model | null>(null)
    const isLoading = ref(false)
    const error = ref<string | null>(null)

    const modelCount = computed(() => models.value.length)

    const completedModels = computed(() =>
        models.value.filter((model) => model.training_status === 'completed')
    )

    const trainingModels = computed(() =>
        models.value.filter((model) => model.training_status === 'training' || model.training_status === 'pending')
    )

    const uploadModel = async (formData: FormData) => {
        isLoading.value = true
        error.value = null
        try {
            const response = await modelApi.uploadModel(formData)
            models.value.push(response.data.data)
            return response.data
        } catch (err: any) {
            error.value = err.response?.data?.message || '上传模型失败'
            throw err
        } finally {
            isLoading.value = false
        }
    }

    const fetchModels = async () => {
        isLoading.value = true
        error.value = null
        try {
            const response = await modelApi.getModelList()
            models.value = response.data.data
            return response.data
        } catch (err: any) {
            error.value = err.response?.data?.message || err.message || '获取模型列表失败'
            throw err
        } finally {
            isLoading.value = false
        }
    }

    const deleteModel = async (modelId: string) => {
        isLoading.value = true
        error.value = null
        try {
            const response = await modelApi.deleteModel(modelId)
            models.value = models.value.filter((model) => model.model_id !== modelId)
            return response.data
        } catch (err: any) {
            error.value = err.response?.data?.message || err.message || '删除模型失败'
            throw err
        } finally {
            isLoading.value = false
        }
    }

    const setCurrentModel = (model: Model | null) => {
        currentModel.value = model
    }

    const clearError = () => {
        error.value = null
    }

    const refreshModel = async (modelId: string) => {
        try {
            const response = await modelApi.getModelList()
            const updatedModel = response.data.data.find((model: Model) => model.model_id === modelId)
            if (updatedModel) {
                const index = models.value.findIndex((model) => model.model_id === modelId)
                if (index !== -1) {
                    models.value[index] = updatedModel
                }
            }
        } catch (err: any) {
            error.value = '刷新模型信息失败'
        }
    }

    return {
        models,
        currentModel,
        isLoading,
        error,
        modelCount,
        completedModels,
        trainingModels,
        uploadModel,
        fetchModels,
        deleteModel,
        setCurrentModel,
        clearError,
        refreshModel,
    }

})