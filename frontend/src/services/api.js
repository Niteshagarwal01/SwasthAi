import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: BASE, timeout: 15000 })

export const getAnalyticsSummary = () => api.get('/api/analytics/summary').then(r => r.data)
export const getTopSymptoms = (days = 30) => api.get(`/api/analytics/symptoms?days=${days}`).then(r => r.data)
export const getRegional = (days = 30) => api.get(`/api/analytics/regional?days=${days}`).then(r => r.data)
export const getTimeline = (days = 30) => api.get(`/api/analytics/timeline?days=${days}`).then(r => r.data)
export const getAlerts = () => api.get('/api/analytics/alerts').then(r => r.data)
export const getChannels = () => api.get('/api/analytics/channels').then(r => r.data)

export const getCases = (params = {}) => api.get('/api/cases', { params }).then(r => r.data)
export const getCase = (id) => api.get(`/api/cases/${id}`).then(r => r.data)

export const simulateWhatsApp = (phone, message) =>
  api.post('/api/simulate/whatsapp', { phone, message }).then(r => r.data)
