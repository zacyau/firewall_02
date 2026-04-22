<template>
  <div class="device-list">
    <div class="page-header">
      <div class="flex flex-between">
        <div>
          <h1 class="page-title">🖥️ 设备管理</h1>
          <p class="page-description">管理所有注册的防火墙设备</p>
        </div>
        <router-link to="/devices/register" class="btn btn-primary">
          + 注册新设备
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else-if="devices.length === 0" class="card empty-state">
      <div class="empty-state-icon">🖥️</div>
      <h3>暂无设备</h3>
      <p>点击下方按钮注册第一个防火墙设备</p>
      <router-link to="/devices/register" class="btn btn-primary mt-4">
        注册设备
      </router-link>
    </div>

    <div v-else>
      <div class="card">
        <table class="table">
          <thead>
            <tr>
              <th>设备名称</th>
              <th>厂商</th>
              <th>IP地址</th>
              <th>直连网段</th>
              <th>路由数</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="device in devices" :key="device.id">
              <td><strong>{{ device.name }}</strong></td>
              <td>
                <span class="vendor-badge" :class="getVendorClass(device.vendor)">
                  {{ device.vendor.toUpperCase() }}
                </span>
              </td>
              <td>{{ device.ip }}:{{ device.port }}</td>
              <td>
                <span class="badge badge-info">{{ device.connected_networks?.length || 0 }}</span>
              </td>
              <td>
                <span class="badge badge-warning">{{ device.routing_table?.length || 0 }}</span>
              </td>
              <td>
                <div class="status-indicator">
                  <span :class="['status-dot', device.status]"></span>
                  <span>{{ device.status === 'online' ? '在线' : '离线' }}</span>
                </div>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    class="btn btn-warning" 
                    @click="editDevice(device)"
                  >
                    ✏️ 编辑
                  </button>
                  <button 
                    class="btn btn-primary" 
                    @click="checkHeartbeat(device.name)"
                    :disabled="checking === device.name"
                  >
                    {{ checking === device.name ? '检测中...' : '🔍 心跳' }}
                  </button>
                  <button 
                    class="btn btn-danger" 
                    @click="confirmDelete(device.name)"
                    :disabled="deleting === device.name"
                  >
                    🗑️ 删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 心跳检测结果弹窗 -->
    <div v-if="showHeartbeatModal" class="modal-overlay" @click="showHeartbeatModal = false">
      <div class="modal-content" @click.stop>
        <h3>🔍 心跳检测结果</h3>
        <div class="modal-body">
          <div v-if="heartbeatResult.loading" class="loading">检测中...</div>
          <div v-else-if="heartbeatResult.error" class="error-message">
            {{ heartbeatResult.error }}
          </div>
          <div v-else>
            <div class="result-item">
              <strong>设备名称：</strong>
              <span>{{ heartbeatResult.device_name }}</span>
            </div>
            <div class="result-item">
              <strong>状态：</strong>
              <span :class="['badge', heartbeatResult.status === 'online' ? 'badge-success' : 'badge-error']">
                {{ heartbeatResult.status }}
              </span>
            </div>
            <div v-if="heartbeatResult.vendor" class="result-item">
              <strong>厂商：</strong>
              <span>{{ heartbeatResult.vendor }}</span>
            </div>
            <div v-if="heartbeatResult.ip" class="result-item">
              <strong>IP：</strong>
              <span>{{ heartbeatResult.ip }}</span>
            </div>
            <div v-if="heartbeatResult.message" class="result-item">
              <strong>消息：</strong>
              <span>{{ heartbeatResult.message }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary" @click="showHeartbeatModal = false">关闭</button>
        </div>
      </div>
    </div>

    <!-- 编辑设备弹窗 -->
    <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
      <div class="modal-content modal-large" @click.stop>
        <h3>✏️ 编辑设备</h3>
        <div class="modal-body">
          <form @submit.prevent="submitEdit">
            <div class="grid grid-2">
              <div class="form-group">
                <label class="form-label">设备名称</label>
                <input 
                  v-model="editForm.name"
                  type="text" 
                  class="form-input" 
                  placeholder="设备名称"
                  required
                  disabled
                  style="background-color: #f5f5f5; cursor: not-allowed;"
                />
                <small style="color: #999; font-size: 12px;">设备名称不可修改</small>
              </div>

              <div class="form-group">
                <label class="form-label">厂商</label>
                <select v-model="editForm.vendor" class="form-select" required>
                  <option value="">请选择厂商</option>
                  <option value="huawei">华为</option>
                  <option value="hillstone">山石</option>
                  <option value="h3c">新华三</option>
                  <option value="juniper">瞻博</option>
                </select>
              </div>
            </div>

            <div class="grid grid-2">
              <div class="form-group">
                <label class="form-label">IP地址 *</label>
                <input 
                  v-model="editForm.ip"
                  type="text" 
                  class="form-input" 
                  placeholder="例如：192.168.1.10"
                  required
                />
              </div>

              <div class="form-group">
                <label class="form-label">端口</label>
                <input 
                  v-model="editForm.port"
                  type="number" 
                  class="form-input" 
                  placeholder="默认：22"
                />
              </div>
            </div>

            <div class="grid grid-2">
              <div class="form-group">
                <label class="form-label">用户名</label>
                <input 
                  v-model="editForm.username"
                  type="text" 
                  class="form-input" 
                  placeholder="SSH用户名"
                />
              </div>

              <div class="form-group">
                <label class="form-label">密码</label>
                <input 
                  v-model="editForm.password"
                  type="password" 
                  class="form-input" 
                  placeholder="SSH密码"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">位置</label>
              <input 
                v-model="editForm.location"
                type="text" 
                class="form-input" 
                placeholder="例如：数据中心A"
              />
            </div>

            <div class="form-section">
              <h4>🌐 直连网段配置</h4>
              <div class="form-group">
                <label class="form-label">直连网段 (YAML格式)</label>
                <textarea 
                  v-model="connectedNetworksYaml"
                  class="form-input" 
                  rows="6"
                  placeholder="- network: 192.168.1.0/24
  zone: trust
  interface: GE0/0/1"
                  style="font-family: monospace;"
                ></textarea>
                <small>格式：YAML 列表，每项包含 network、zone、interface</small>
              </div>
            </div>

            <div class="form-section">
              <h4>🛤️ 路由表配置</h4>
              <div class="form-group">
                <label class="form-label">路由表 (YAML格式)</label>
                <textarea 
                  v-model="routingTableYaml"
                  class="form-input" 
                  rows="6"
                  placeholder="- destination: 172.25.0.0/16
  next_hop: other_fw
  zone: untrust"
                  style="font-family: monospace;"
                ></textarea>
                <small>格式：YAML 列表，每项包含 destination、next_hop、zone</small>
              </div>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="editSubmitting">
                {{ editSubmitting ? '保存中...' : '✅ 保存修改' }}
              </button>
              <button type="button" class="btn" @click="showEditModal = false" style="background: #999; color: white;">
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { deviceAPI } from '../services/api'
import yaml from 'js-yaml'

const devices = ref([])
const loading = ref(false)
const error = ref('')
const checking = ref('')
const deleting = ref('')
const showHeartbeatModal = ref(false)
const heartbeatResult = ref({})
const showEditModal = ref(false)
const editingDevice = ref({})
const editForm = ref({
  name: '',
  vendor: '',
  ip: '',
  port: 22,
  username: '',
  password: '',
  location: '',
  connected_networks: [],
  routing_table: []
})
const connectedNetworksYaml = ref('')
const routingTableYaml = ref('')
const editSubmitting = ref(false)

const loadDevices = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await deviceAPI.getAll()
    devices.value = response.data.devices || []
  } catch (err) {
    error.value = '加载设备列表失败：' + (err.message || '未知错误')
    console.error('加载设备失败:', err)
  } finally {
    loading.value = false
  }
}

const checkHeartbeat = async (deviceName) => {
  checking.value = deviceName
  heartbeatResult.value = { loading: true }
  showHeartbeatModal.value = true
  
  try {
    const response = await deviceAPI.checkHeartbeat(deviceName)
    heartbeatResult.value = response.data
    await loadDevices()
  } catch (err) {
    heartbeatResult.value = {
      error: '心跳检测失败：' + (err.message || '未知错误')
    }
    console.error('心跳检测失败:', err)
  } finally {
    checking.value = ''
  }
}

const confirmDelete = async (deviceName) => {
  if (!confirm(`确定要删除设备 "${deviceName}" 吗？`)) {
    return
  }
  
  deleting.value = deviceName
  try {
    await deviceAPI.delete(deviceName)
    await loadDevices()
  } catch (err) {
    alert('删除失败：' + (err.message || '未知错误'))
    console.error('删除设备失败:', err)
  } finally {
    deleting.value = ''
  }
}

const getVendorClass = (vendor) => {
  const classes = {
    'huawei': 'vendor-huawei',
    'hillstone': 'vendor-hillstone',
    'h3c': 'vendor-h3c',
    'juniper': 'vendor-juniper'
  }
  return classes[vendor] || ''
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

const editDevice = (device) => {
  editingDevice.value = device
  editForm.value = {
    name: device.name,
    vendor: device.vendor,
    ip: device.ip,
    port: device.port || 22,
    username: device.username || '',
    password: device.password || '',
    location: device.location || '',
    connected_networks: device.connected_networks || [],
    routing_table: device.routing_table || []
  }
  connectedNetworksYaml.value = yaml.dump(device.connected_networks || [])
  routingTableYaml.value = yaml.dump(device.routing_table || [])
  showEditModal.value = true
}

const showDeviceDetail = (device) => {
  editingDevice.value = device
  editForm.value = {
    name: device.name,
    vendor: device.vendor,
    ip: device.ip,
    port: device.port || 22,
    username: device.username || '',
    password: device.password || '',
    location: device.location || '',
    connected_networks: device.connected_networks || [],
    routing_table: device.routing_table || []
  }
  connectedNetworksYaml.value = yaml.dump(device.connected_networks || [])
  routingTableYaml.value = yaml.dump(device.routing_table || [])
  showEditModal.value = true
}

const submitEdit = async () => {
  editSubmitting.value = true
  try {
    try {
      editForm.value.connected_networks = yaml.load(connectedNetworksYaml.value || '[]')
    } catch (e) {
      alert('❌ 直连网段 YAML 格式错误')
      editSubmitting.value = false
      return
    }
    
    try {
      editForm.value.routing_table = yaml.load(routingTableYaml.value || '[]')
    } catch (e) {
      alert('❌ 路由表 YAML 格式错误')
      editSubmitting.value = false
      return
    }
    
    const response = await deviceAPI.register(editForm.value)
    if (response.data.status === 'updated' || response.data.status === 'registered') {
      alert('✅ 设备更新成功！')
      showEditModal.value = false
      await loadDevices()
    }
  } catch (error) {
    alert('❌ 更新失败：' + (error.response?.data?.detail || error.message))
    console.error('更新设备失败:', error)
  } finally {
    editSubmitting.value = false
  }
}

onMounted(() => {
  loadDevices()
})
</script>

<style scoped>
.vendor-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.vendor-huawei {
  background: #e6f7ff;
  color: #1890ff;
}

.vendor-hillstone {
  background: #fff7e6;
  color: #fa8c16;
}

.vendor-h3c {
  background: #f6ffed;
  color: #52c41a;
}

.vendor-juniper {
  background: #fff0f0;
  color: #f5222d;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.modal-content h3 {
  margin-bottom: 16px;
  color: #333;
}

.modal-body {
  margin: 20px 0;
}

.result-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

.result-item:last-child {
  border-bottom: none;
}

.modal-large {
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-footer {
  text-align: right;
  margin-top: 20px;
}

.form-section {
  margin: 20px 0;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 6px;
}

.form-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
  border-bottom: 2px solid #1890ff;
  padding-bottom: 8px;
}

textarea.form-input {
  resize: vertical;
  min-height: 80px;
}

.form-section small {
  display: block;
  margin-top: 4px;
  color: #999;
  font-size: 12px;
}
</style>
