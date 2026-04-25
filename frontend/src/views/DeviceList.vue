<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">设备管理</h1>
        <p class="page-desc">管理所有注册的防火墙设备</p>
      </div>
      <router-link to="/devices/register" class="btn-primary">注册新设备</router-link>
    </div>

    <div class="card">
      <div v-if="loading" class="py-12 text-center text-sm text-gray-400">加载中...</div>
      <div v-else-if="error" class="px-6 py-4 text-sm text-danger-500">{{ error }}</div>
      <div v-else-if="devices.length === 0" class="empty-state py-16">
        <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
        <p class="text-sm text-gray-400 mb-3">暂无设备</p>
        <router-link to="/devices/register" class="btn-primary btn-sm">注册设备</router-link>
      </div>

      <div v-else class="table-container">
        <table class="data-table">
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
              <td class="font-medium text-gray-900">{{ device.name }}</td>
              <td><span :class="vendorBadge(device.vendor)">{{ device.vendor.toUpperCase() }}</span></td>
              <td class="font-mono text-xs">{{ device.ip }}:{{ device.port }}</td>
              <td><span class="badge-primary">{{ device.connected_networks?.length || 0 }}</span></td>
              <td><span class="badge-warning">{{ device.routing_table?.length || 0 }}</span></td>
              <td>
                <span class="inline-flex items-center gap-1.5 text-sm">
                  <span :class="['w-1.5 h-1.5 rounded-full', device.status === 'online' ? 'bg-success-500' : 'bg-gray-300']"></span>
                  {{ device.status === 'online' ? '在线' : '离线' }}
                </span>
              </td>
              <td>
                <div class="flex items-center gap-2">
                  <button class="btn-default btn-sm" @click="editDevice(device)">编辑</button>
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

      <div v-if="showEditModal" class="modal-backdrop" @click.self="showEditModal = false">
        <div class="modal-panel-xl" @click.stop>
          <div class="modal-header">
            <h3 class="text-base font-semibold text-gray-900">编辑设备</h3>
            <button class="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100" @click="showEditModal = false">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitEdit" class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="form-label">设备名称</label>
                  <input v-model="editForm.name" type="text" class="form-input" disabled />
                </div>
                <div>
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
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="form-label">IP地址 *</label>
                  <input v-model="editForm.ip" type="text" class="form-input" placeholder="例如：192.168.1.10" required />
                </div>
                <div>
                  <label class="form-label">端口</label>
                  <input v-model="editForm.port" type="number" class="form-input" placeholder="默认：22" />
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="form-label">用户名</label>
                  <input v-model="editForm.username" type="text" class="form-input" placeholder="SSH用户名" />
                </div>
                <div>
                  <label class="form-label">密码</label>
                  <input v-model="editForm.password" type="password" class="form-input" placeholder="SSH密码" />
                </div>
              </div>
              <div>
                <label class="form-label">位置</label>
                <input v-model="editForm.location" type="text" class="form-input" placeholder="例如：数据中心A" />
              </div>
              <div>
                <label class="form-label">直连网段 (YAML)</label>
                <textarea v-model="connectedNetworksYaml" class="form-input font-mono" rows="4" placeholder="- network: 192.168.1.0/24&#10;  zone: trust&#10;  interface: GE0/0/1"></textarea>
              </div>
              <div>
                <label class="form-label">路由表 (YAML)</label>
                <textarea v-model="routingTableYaml" class="form-input font-mono" rows="4" placeholder="- destination: 172.25.0.0/16&#10;  next_hop: other_fw&#10;  zone: untrust"></textarea>
              </div>
              <div class="flex justify-end gap-3 pt-2">
                <button type="button" class="btn-default" @click="showEditModal = false">取消</button>
                <button type="submit" class="btn-primary" :disabled="editSubmitting">{{ editSubmitting ? '保存中...' : '保存修改' }}</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Teleport>
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
const editForm = ref({ name: '', vendor: '', ip: '', port: 22, username: '', password: '', location: '', connected_networks: [], routing_table: [] })
const connectedNetworksYaml = ref('')
const routingTableYaml = ref('')
const editSubmitting = ref(false)

const vendorBadge = (v) => ({ huawei: 'badge-primary', hillstone: 'badge-warning', h3c: 'badge-success', juniper: 'badge-danger' }[v] || 'badge-gray')

const loadDevices = async () => {
  loading.value = true; error.value = ''
  try { const r = await deviceAPI.getAll(); devices.value = r.data.devices || [] }
  catch (e) { error.value = '加载设备列表失败：' + (e.message || '未知错误') }
  finally { loading.value = false }
}

const checkHeartbeat = async (name) => {
  checking.value = name; heartbeatResult.value = { loading: true }; showHeartbeatModal.value = true
  try { const r = await deviceAPI.checkHeartbeat(name); heartbeatResult.value = r.data; await loadDevices() }
  catch (e) { heartbeatResult.value = { error: '心跳检测失败：' + (e.message || '未知错误') } }
  finally { checking.value = '' }
}

const confirmDelete = async (name) => {
  if (!confirm(`确定要删除设备 "${name}" 吗？`)) return
  deleting.value = name
  try { await deviceAPI.delete(name); await loadDevices() }
  catch (e) { alert('删除失败：' + (e.message || '未知错误')) }
  finally { deleting.value = '' }
}

const editDevice = (device) => {
  editForm.value = { name: device.name, vendor: device.vendor, ip: device.ip, port: device.port || 22, username: device.username || '', password: device.password || '', location: device.location || '', connected_networks: device.connected_networks || [], routing_table: device.routing_table || [] }
  connectedNetworksYaml.value = yaml.dump(device.connected_networks || [])
  routingTableYaml.value = yaml.dump(device.routing_table || [])
  showEditModal.value = true
}

const submitEdit = async () => {
  editSubmitting.value = true
  try {
    try { editForm.value.connected_networks = yaml.load(connectedNetworksYaml.value || '[]') } catch { alert('直连网段 YAML 格式错误'); editSubmitting.value = false; return }
    try { editForm.value.routing_table = yaml.load(routingTableYaml.value || '[]') } catch { alert('路由表 YAML 格式错误'); editSubmitting.value = false; return }
    const r = await deviceAPI.register(editForm.value)
    if (r.data.status === 'updated' || r.data.status === 'registered') { alert('设备更新成功！'); showEditModal.value = false; await loadDevices() }
  } catch (e) { alert('更新失败：' + (e.response?.data?.detail || e.message)) }
  finally { editSubmitting.value = false }
}

onMounted(loadDevices)
</script>
