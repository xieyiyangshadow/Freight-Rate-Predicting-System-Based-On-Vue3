import client from './client'

export const uploadModel = (formData: FormData) => {
    return client.post('/model/upload/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })
}

export const getModelList = () => {
    return client.get('/model/list/')
}

export const deleteModel = (modelId: string) => {
    return client.delete(`/model/delete/${modelId}/`)
}