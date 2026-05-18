import client from './client'
import type { CreatePredictionRequest, PredictionTask } from '@/types/prediction'

export const createPredictionTask = (data: CreatePredictionRequest) =>
    client.post('/prediction/create/', data)

export const getPredictionList = () =>
    client.get('/prediction/list/')

export const getPredictionDetail = (taskId: string) =>
    client.get(`/prediction/detail/${taskId}/`)