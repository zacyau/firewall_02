<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">地址组管理</h1>
        <p class="page-desc">管理 IP 地址组，用于策略配置</p>
      </div>
      <router-link to="/groups/address/create" class="btn-primary">创建地址组</router-link>
    </div>

    <div v-if="loading" class="py-12 text-center text-sm text-gray-400">加载中...</div>
    <div v-else-if="error" class="px-6 py-4 text-sm text-danger-500">{{ error }}</div>
    <div v-else-if="groups.length === 0" class="card empty-state py-16">
      <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
      <p class="text-sm text-gray-400 mb-3">暂无地址组</p>
      <router-link to="/groups/address/create" class="btn-primary btn-sm">创建地址组</router-link>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="group in groups" :key="group.id" class="card">
        <div class="card-body">
          <div class="flex items-start justify-between mb-3">
            <div>
              <h4 class="text-sm font-semibold text-gray-900">{{ group.name }}</h4>
              <p class="text-xs text-gray-400 mt-0.5">{{ group.description || '无描述' }}</p>
            </div>
            <div class="flex items-center gap-1">
              <button class="btn-default btn-sm" @click="editGroup(group)">编辑</button>
              <button class="btn-danger btn-sm" @click="confirmDelete(group)">删除</button>
            </div>
          </div>
          <div class="flex items-center gap-2 mb-3 text-xs text-gray-500">
            <span>地址数量：</span><span class="badge-primary">{{ group.addresses?.length || 0 }}</span>
          </div>
          <div class="flex flex-wrap gap-1.5 mb-4">
            <span v-for="(addr, idx) in (group.addresses || [])" :key="idx" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-primary-50 text-primary-600">
              {{ addr }}
            </span>
          </div>
          <button class="btn-primary btn-sm w-full" @click="showDeployModal(group)" :disabled="deployLoading[group.name]">
            {{ deployLoading[group.name] ? '加载中...' : '配置到防火墙' }}
          </button>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showEditModal" class="modal-backdrop" @click.self="showEditModal = false">
        <div class="modal-panel" @click.stop>
          <div class="modal-header">
            <h3 class="text-base font-semibold text-gray-900">编辑地址组</h3>
            <button class="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100" @click="showEditModal = false">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitEdit" class="space-y-4">
              <div><label class="form-label">组名称</label><input v-model="editForm.name" type="text" class="form-input" disabled /></div>
              <div><label class="form-label">描述</label><input v-model="editForm.description" type="text" class="form-input" /></div>
              <div>
                <label class="form-label">地址列表</label>
                <textarea v-model="addressesText" class="form-input font-mono" rows="6" placeholder="192.168.1.1&#10;192.168.1.2&#10;10.0.0.0/24"></textarea>
                <p class="text-xs text-gray-400 mt-1">每行一个IP地址或网段(CIDR格式)</p>
              </div>
              <div class="flex justify-end gap-3 pt-2">
                <button type="button" class="btn-default" @click="showEditModal = false">取消</button>
                <button type="submit" class="btn-primary" :disabled="submitting">{{ submitting ? '保存中...' : '保存修改' }}</button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <div v-if="showDeployModalFlag" class="modal-backdrop" @click.self="closeDeployModal">
        <div class="modal-panel-xl" @click.stop>
          <div class="modal-header">
            <h3 class="text-base font-semibold text-gray-900">配置地址组到防火墙 - {{ currentGroup?.name }}</h3>
            <button class="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100" @click="closeDeployModal">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="deployLoading[currentGroup?.name]" class="py-8 text-center text-sm text-gray-400">加载设备配置状态...</div>
            <div v-else-if="deployError" class="text-sm text-danger-500">{{ deployError }}</div>
            <div v-else>
              <div class="flex items-center gap-4 mb-4">
                <span class="text-xs text-gray-500">总设备: <span class="badge-gray">{{ deployDevices.length }}</span></span>
                <span class="text-xs text-gray-500">已配置: <span class="badge-success">{{ deployDevices.filter(d => d.status === 'created').length }}</span></span>
                <span class="text-xs text-gray-500">待配置: <span class="badge-warning">{{ deployDevices.filter(d => d.status === 'pending').length }}</span></span>
              </div>

              <button v-if="deployDevices.some(d => d.status === 'pending')" class="btn-primary btn-sm mb-4" @click="applyToAll" :disabled="applyingAll">
                {{ applyingAll ? '批量应用中...' : '批量应用到所有设备' }}
              </button>

              <div class="flex gap-4">
                <div class="flex-1 min-w-0 space-y-2">
                  <div v-for="device in deployDevices" :key="device.device_name" class="flex items-center justify-between px-3 py-2.5 rounded-lg border border-gray-200">
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ device.device_name }}</div>
                      <div class="text-xs text-gray-400">厂商: {{ device.vendor }}</div>
                    </div>
                    <div class="flex items-center gap-2">
                      <span v-if="device.status === 'created'" class="badge-success">已配置</span>
                      <span v-else class="badge-warning">待配置</span>
                      <button v-if="device.status === 'pending'" class="btn-primary btn-sm" @click="applyToDevice(device.device_name)" :disabled="applyingDevice[device.device_name]">
                        {{ applyingDevice[device.device_name] ? '应用中...' : '应用' }}
                      </button>
                    </div>
                  </div>
                </div>

                <div v-if="configScript" class="flex-[1.2] min-w-0">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-medium text-gray-700">配置脚本预览</span>
                    <select v-model="selectedDevice" @change="updateConfigPreview" class="form-select w-48 text-xs">
                      <option v-for="device in deployDevices" :key="device.device_name" :value="device.device_name">
                        {{ device.device_name }} ({{ device.vendor }})
                      </option>
                    </select>
                  </div>
                  <pre class="code-block max-h-96 overflow-y-auto">{{ configScript }}</pre>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-default" @click="closeDeployModal">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { addressGroupAPI } from '../services/api'

const groups = ref([])
const loading = ref(false)
const error = ref('')
const showEditModal = ref(false)
const editForm = ref({ id: null, name: '', description: '', addresses: [] })
const addressesText = ref('')
const submitting = ref(false)
const showDeployModalFlag = ref(false)
const currentGroup = ref(null)
const deployDevices = ref([])
const deployLoading = ref({})
const deployError = ref('')
const applyingDevice = ref({})
const applyingAll = ref(false)
const configScript = ref('')
const selectedDevice = ref('')

const loadGroups = async () => {
  loading.value = true; error.value = ''
  try { const r = await addressGroupAPI.getAll(); groups.value = r.data.groups || [] }
  catch (e) { error.value = '加载地址组失败：' + (e.message || '未知错误') }
  finally { loading.value = false }
}

const editGroup = (group) => {
  editForm.value = { ...group }; addressesText.value = (group.addresses || []).join('\n'); showEditModal.value = true
}

const submitEdit = async () => {
  submitting.value = true
  try {
    const addrs = addressesText.value.split('\n').map(a => a.trim()).filter(a => a)
    await addressGroupAPI.update(editForm.value.name, { name: editForm.value.name, description: editForm.value.description, addresses: addrs })
    showEditModal.value = false; await loadGroups()
  } catch (e) { alert('保存失败：' + (e.response?.data?.detail || e.message)) }
  finally { submitting.value = false }
}

const confirmDelete = async (group) => {
  if (!confirm(`确定要删除地址组 "${group.name}" 吗？`)) return
  try { await addressGroupAPI.delete(group.name); await loadGroups() }
  catch (e) { alert('删除失败：' + (e.message || '未知错误')) }
}

const showDeployModal = async (group) => {
  currentGroup.value = group; showDeployModalFlag.value = true; deployError.value = ''; configScript.value = ''; selectedDevice.value = ''
  deployLoading.value[group.name] = true
  try {
    const r = await addressGroupAPI.generateConfigs(group.name)
    if (r.data.status === 'success') {
      deployDevices.value = r.data.devices || []
      if (deployDevices.value.length > 0) {
        const first = deployDevices.value.find(d => d.status === 'pending') || deployDevices.value[0]
        selectedDevice.value = first.device_name; configScript.value = first.config_script || ''
      }
    } else { deployError.value = r.data.message || '生成配置失败' }
  } catch (e) { deployError.value = '生成配置失败：' + (e.response?.data?.detail || e.message) }
  finally { deployLoading.value[group.name] = false }
}

const updateConfigPreview = () => {
  const d = deployDevices.value.find(d => d.device_name === selectedDevice.value)
  if (d) configScript.value = d.config_script || ''
}

const closeDeployModal = () => { showDeployModalFlag.value = false; currentGroup.value = null; deployDevices.value = []; configScript.value = ''; selectedDevice.value = '' }

const applyToDevice = async (deviceName) => {
  applyingDevice.value[deviceName] = true
  try {
    await addressGroupAPI.applyConfig(currentGroup.value.name, deviceName)
    const d = deployDevices.value.find(d => d.device_name === deviceName)
    if (d) d.status = 'created'
    updateConfigPreview()
  } catch (e) { alert('应用失败：' + (e.response?.data?.detail || e.message)) }
  finally { applyingDevice.value[deviceName] = false }
}

const applyToAll = async () => {
  applyingAll.value = true
  try {
    const r = await addressGroupAPI.applyAll(currentGroup.value.name)
    if (r.data.results) {
      for (const res of r.data.results) {
        if (res.status === 'success') { const d = deployDevices.value.find(d => d.device_name === res.device_name); if (d) d.status = 'created' }
      }
    }
    updateConfigPreview()
  } catch (e) { alert('批量应用失败：' + (e.response?.data?.detail || e.message)) }
  finally { applyingAll.value = false }
}

onMounted(loadGroups)
</script>
