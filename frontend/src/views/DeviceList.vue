<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">设备管理</h1>
        <p class="page-desc">防火墙设备由数据库统一管理</p>
      </div>
      <div class="flex gap-2">
        <router-link to="/devices/register" class="btn-primary">添加设备</router-link>
      </div>
    </div>

    <div class="card">
      <div class="bg-amber-50 border border-amber-200 rounded-md p-4 mb-4">
        <div class="flex items-start gap-3">
          <svg class="w-5 h-5 text-amber-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 class="text-sm font-medium text-amber-800">数据库驱动模式</h4>
            <p class="text-sm text-amber-700 mt-1">
              设备信息存储在数据库中，首次启动时从配置文件种子自动导入。所有修改实时生效。
            </p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="py-12 text-center text-sm text-gray-400">加载中...</div>
      <div v-else-if="error" class="px-6 py-4 text-sm text-danger-500">{{ error }}</div>
      <div v-else-if="devices.length === 0" class="empty-state py-16">
        <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
        <p class="text-sm text-gray-400 mb-3">暂无设备</p>
        <router-link to="/devices/register" class="btn-primary btn-sm">添加设备</router-link>
      </div>

      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>设备名称</th>
              <th>厂商</th>
              <th>IP地址</th>
              <th>描述</th>
              <th>区域类型</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="device in devices" :key="device.name">
              <td class="font-medium text-gray-900">{{ device.name }}</td>
              <td><span :class="vendorBadge(device.vendor)">{{ device.vendor.toUpperCase() }}</span></td>
              <td class="font-mono text-xs">{{ device.ip }}:{{ device.port }}</td>
              <td class="text-sm text-gray-500">{{ device.description || '-' }}</td>
              <td>
                <div class="flex flex-wrap gap-1">
                  <span v-for="zoneType in getZoneTypes(device.zones)" :key="zoneType" class="badge-primary text-xs">{{ zoneType }}</span>
                </div>
              </td>
              <td>
                <div class="flex items-center gap-2">
                  <router-link :to="'/devices/register?name=' + device.name" class="btn-default btn-sm">编辑</router-link>
                  <button class="btn-default btn-sm" @click="showConfig(device)" title="查看配置">配置</button>
                  <button class="btn-default btn-sm" @click="checkHeartbeat(device.name)" :disabled="checking === device.name">
                    {{ checking === device.name ? '检测中...' : '心跳' }}
                  </button>
                  <button class="btn-danger btn-sm" @click="confirmDelete(device.name)" :disabled="deleting === device.name">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showHeartbeatModal" class="modal-backdrop" @click.self="showHeartbeatModal = false">
        <div class="modal-panel" @click.stop>
          <div class="modal-header">
            <h3 class="text-base font-semibold text-gray-900">心跳检测结果</h3>
            <button class="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100" @click="showHeartbeatModal = false">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="heartbeatResult.loading" class="text-center text-sm text-gray-400 py-4">检测中...</div>
            <div v-else-if="heartbeatResult.error" class="text-sm text-danger-500">{{ heartbeatResult.error }}</div>
            <div v-else class="space-y-2 text-sm">
              <div class="flex gap-2"><span class="text-gray-500 w-16 shrink-0">设备：</span><span>{{ heartbeatResult.device_name }}</span></div>
              <div class="flex gap-2"><span class="text-gray-500 w-16 shrink-0">状态：</span><span :class="heartbeatResult.status === 'online' ? 'text-success-600' : 'text-danger-600'">{{ heartbeatResult.status }}</span></div>
              <div v-if="heartbeatResult.vendor" class="flex gap-2"><span class="text-gray-500 w-16 shrink-0">厂商：</span><span>{{ heartbeatResult.vendor }}</span></div>
              <div v-if="heartbeatResult.ip" class="flex gap-2"><span class="text-gray-500 w-16 shrink-0">IP：</span><span class="font-mono">{{ heartbeatResult.ip }}</span></div>
              <div v-if="heartbeatResult.message" class="flex gap-2"><span class="text-gray-500 w-16 shrink-0">消息：</span><span>{{ heartbeatResult.message }}</span></div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-default" @click="showHeartbeatModal = false">关闭</button>
          </div>
        </div>
      </div>

      <div v-if="showConfigModal" class="modal-backdrop" @click.self="showConfigModal = false">
        <div class="modal-panel-xl" @click.stop>
          <div class="modal-header">
            <h3 class="text-base font-semibold text-gray-900">设备配置详情 - {{ selectedDevice?.name }}</h3>
            <button class="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100" @click="showConfigModal = false">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <pre class="bg-gray-900 text-gray-100 p-4 rounded-md text-xs overflow-x-auto">{{ deviceConfigYaml }}</pre>
          </div>
          <div class="modal-footer">
            <button class="btn-default" @click="showConfigModal = false">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { deviceAPI } from '../services/api'

const devices = ref([])
const loading = ref(false)
const error = ref('')
const checking = ref('')
const deleting = ref('')
const showHeartbeatModal = ref(false)
const heartbeatResult = ref({})
const showConfigModal = ref(false)
const selectedDevice = ref(null)

const vendorBadge = (v) => ({ huawei: 'badge-primary', hillstone: 'badge-warning', h3c: 'badge-success', juniper: 'badge-danger' }[v] || 'badge-gray')

const getZoneTypes = (zones) => {
  if (!zones) return []
  return Object.keys(zones)
}

const deviceConfigYaml = computed(() => {
  if (!selectedDevice.value) return ''
  return JSON.stringify(selectedDevice.value, null, 2)
})

const loadDevices = async () => {
  loading.value = true; error.value = ''
  try { const r = await deviceAPI.getAll(); devices.value = r.data.devices || [] }
  catch (e) { error.value = '加载设备列表失败：' + (e.message || '未知错误') }
  finally { loading.value = false }
}

const checkHeartbeat = async (name) => {
  checking.value = name; heartbeatResult.value = { loading: true }; showHeartbeatModal.value = true
  try { const r = await deviceAPI.checkHeartbeat(name); heartbeatResult.value = r.data }
  catch (e) { heartbeatResult.value = { error: '心跳检测失败：' + (e.message || '未知错误') } }
  finally { checking.value = '' }
}

const confirmDelete = async (name) => {
  if (!confirm(`确定要删除设备 "${name}" 吗？删除后将无法恢复。`)) return
  deleting.value = name
  try {
    const r = await deviceAPI.delete(name)
    if (r.data.status === 'success') {
      alert('设备已删除')
      await loadDevices()
    } else {
      alert('删除失败：' + (r.data.detail || r.data.message))
    }
  } catch (e) { alert('删除失败：' + (e.response?.data?.detail || e.message)) }
  finally { deleting.value = '' }
}

const showConfig = (device) => {
  selectedDevice.value = device
  showConfigModal.value = true
}

onMounted(loadDevices)
</script>
