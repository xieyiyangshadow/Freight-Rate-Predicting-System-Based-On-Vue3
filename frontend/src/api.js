import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const user = localStorage.getItem('freight_current_user')
  if (user) {
    config.headers['X-Client-User'] = user
  }
  return config
})

export function getCurrentUser() {
  const raw = localStorage.getItem('freight_current_user')
  return raw ? JSON.parse(raw) : null
}

export function setCurrentUser(user) {
  localStorage.setItem('freight_current_user', JSON.stringify(user))
  window.dispatchEvent(new CustomEvent('freight-auth-changed', { detail: user }))
}

export function clearCurrentUser() {
  localStorage.removeItem('freight_current_user')
  window.dispatchEvent(new CustomEvent('freight-auth-changed', { detail: null }))
}

export default api

// Dataset APIs
export async function getDatasets() {
  return api.get('/models/datasets/')
}

export async function uploadDataset(formData) {
  return api.post('/models/datasets/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
}

export async function getDataset(id) {
  return api.get(`/models/datasets/${id}/`)
}

export async function updateDataset(id, data) {
  return api.patch(`/models/datasets/${id}/`, data)
}
