import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const configAPI = {
  getAllDevices: () => api.get('/devices'),
  getDevice: (name) => api.get(`/devices/${name}`),
  createDevice: (deviceData) => api.post('/devices/register', deviceData),
  deleteDevice: (name) => api.delete(`/devices/${name}`)
}

export default api
