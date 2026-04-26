import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 设备管理 API
export const deviceAPI = {
  // 获取所有设备
  getAll: () => api.get('/devices'),
  
  // 获取单个设备
  get: (name) => api.get(`/devices/${name}`),
  
  // 注册设备
  register: (deviceData) => api.post('/devices/register', deviceData),
  
  // 删除设备
  delete: (name) => api.delete(`/devices/${name}`),
  
  // 检查心跳
  checkHeartbeat: (name) => api.get(`/devices/${name}/heartbeat`)
}

// 策略管理 API
export const policyAPI = {
  // 生成策略
  generate: (policyData) => api.post('/policies/generate', policyData),
  
  // 生成策略（dry_run模式）
  generateDryRun: (policyData) => api.post('/policies/generate?dry_run=true', policyData),
  
  // 应用策略
  apply: (applyData, simulate = true) => api.post(`/policies/apply?simulate=${simulate}`, applyData),
  
  // 获取所有策略
  getAll: () => api.get('/policies'),
  
  // 获取单个策略
  get: (id) => api.get(`/policies/${id}`),
  
  // 策略验证
  validate: (data) => api.post('/policies/validate', data)
}

// 健康检查
export const healthAPI = {
  check: () => axios.get('/health')
}

// 地址组管理 API
export const addressGroupAPI = {
  getAll: () => api.get('/groups/address'),
  get: (name) => api.get(`/groups/address/${name}`),
  create: (data) => api.post('/groups/address', data),
  update: (name, data) => api.put(`/groups/address/${name}`, data),
  delete: (name) => api.delete(`/groups/address/${name}`),
  generateConfigs: (name) => api.post(`/groups/address/${name}/generate`),
  applyConfig: (name, deviceName) => api.post(`/groups/address/${name}/apply/${deviceName}`),
  applyAll: (name) => api.post(`/groups/address/${name}/apply-all`),
  getStatus: (name) => api.get(`/groups/address/${name}/status`)
}

// 端口组管理 API
export const portGroupAPI = {
  getAll: () => api.get('/groups/port'),
  get: (name) => api.get(`/groups/port/${name}`),
  create: (data) => api.post('/groups/port', data),
  update: (name, data) => api.put(`/groups/port/${name}`, data),
  delete: (name) => api.delete(`/groups/port/${name}`),
  generateConfigs: (name) => api.post(`/groups/port/${name}/generate`),
  applyConfig: (name, deviceName) => api.post(`/groups/port/${name}/apply/${deviceName}`),
  applyAll: (name) => api.post(`/groups/port/${name}/apply-all`),
  getStatus: (name) => api.get(`/groups/port/${name}/status`)
}

export default api
