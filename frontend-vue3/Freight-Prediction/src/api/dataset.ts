import client from './client'

export const uploadDataset = (formData: FormData) => {
    return client.post('/dataset/upload/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    })
}

export const getDatasetList = () => {
    return client.get('/dataset/list/')
}

export const deleteDataset = (datasetId: string) => {
    return client.delete(`/dataset/delete/${datasetId}/`)
}

export const getDatasetDetail = (datasetId: string) => {
    return client.get(`/dataset/detail/${datasetId}/`)
}