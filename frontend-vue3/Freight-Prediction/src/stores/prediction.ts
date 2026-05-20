import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as predictionApi from '@/api/prediction'
import type { PredictionTask, CreatePredictionRequest } from '@/types/prediction'

export const usePredictionStore = defineStore('prediction', () => {
    const tasks = ref<PredictionTask[]>([])
    const currentTask = ref<PredictionTask | null>(null)
    const isLoading = ref(false)
    const error = ref<string | null>(null)
    
    let pollInterval: any = null

    const createPredictionTask = async (data: CreatePredictionRequest) => {
        isLoading.value = true
        error.value = null
        try {
            const response = await predictionApi.createPredictionTask(data)
            const newTask = response.data.task
            tasks.value.unshift(newTask)
            
            currentTask.value = newTask
            startPolling(newTask.task_id)
            
            return response.data
        } catch (err: any) {
            // 尝试解析后端返回的详细错误信息（支持 message 字段或字段级 validation 错误）
            const respData = err.response?.data
            if (!respData) {
                error.value = '创建预测任务失败'
            } else if (typeof respData === 'string') {
                error.value = respData
            } else if (respData.message) {
                error.value = respData.message
            } else if (typeof respData === 'object') {
                // 将对象内的错误扁平化为单条文本
                try {
                    const parts: string[] = []
                    Object.entries(respData).forEach(([k, v]) => {
                        if (Array.isArray(v)) {
                            parts.push(`${k}: ${v.join('; ')}`)
                        } else if (typeof v === 'string') {
                            parts.push(`${k}: ${v}`)
                        } else if (typeof v === 'object' && v !== null) {
                            parts.push(`${k}: ${JSON.stringify(v)}`)
                        }
                    })
                    error.value = parts.join(' | ') || '创建预测任务失败'
                } catch (e) {
                    error.value = '创建预测任务失败'
                }
            } else {
                error.value = '创建预测任务失败'
            }
            throw err
        } finally {
            isLoading.value = false
        }
    }
    
    const startPolling = (taskId: string) => {
        if (pollInterval) return
        
        console.log('开始轮询预测任务状态...')
        
        pollInterval = setInterval(async () => {
            try {
                const response = await predictionApi.getPredictionDetail(taskId)
                const updatedTask = response.data.task
                
                const index = tasks.value.findIndex(t => t.task_id === taskId)
                if (index !== -1) {
                    tasks.value[index] = updatedTask
                }
                
                if (updatedTask.status === 'completed' || updatedTask.status === 'failed') {
                    stopPolling()
                    currentTask.value = updatedTask
                }
            } catch (err) {
                console.error('轮询预测任务失败', err)
            }
        }, 2000)
    }
    
    const stopPolling = () => {
        if (pollInterval) {
            clearInterval(pollInterval)
            pollInterval = null
        }
    }
    
    const fetchTasks = async () => {
        isLoading.value = true
        error.value = null
        try {
            const response = await predictionApi.getPredictionList()
            tasks.value = response.data.tasks
            return response.data
        } catch (err: any) {
            error.value = err.response?.data?.message || '获取预测任务列表失败'
            throw err
        } finally {
            isLoading.value = false
        }
    }
    
    const refreshTask = async (taskId: string) => {
        try {
            const response = await predictionApi.getPredictionDetail(taskId)
            const updatedTask = response.data.task
            
            const index = tasks.value.findIndex(t => t.task_id === taskId)
            if (index !== -1) {
                tasks.value[index] = updatedTask
            }
            
            return updatedTask
        } catch (err: any) {
            error.value = '刷新任务信息失败'
            throw err
        }
    }

    const deletePredictionTask = async (taskId: string) => {
        try {
            await predictionApi.deletePrediction(taskId)
            const index = tasks.value.findIndex(t => t.task_id === taskId)
            if (index !== -1) tasks.value.splice(index, 1)
            if (currentTask.value?.task_id === taskId) currentTask.value = null
            return { status: 'success' }
        } catch (err: any) {
            error.value = err.response?.data?.message || '删除预测任务失败'
            throw err
        }
    }
    
    const clearError = () => {
        error.value = null
    }
    
    const completedTasks = computed(() =>
        (tasks.value || []).filter(t => t?.status === 'completed')
    )

    const runningTasks = computed(() =>
        (tasks.value || []).filter(t => t?.status === 'running' || t?.status === 'pending')
    )
    
    return {
        tasks,
        currentTask,
        isLoading,
        error,
        completedTasks,
        runningTasks,
        createPredictionTask,
        fetchTasks,
        refreshTask,
        clearError,
        startPolling,
        stopPolling,
        deletePredictionTask,
    }
})