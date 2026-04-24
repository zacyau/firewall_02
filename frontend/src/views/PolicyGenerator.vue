<template>
  <div class="policy-generator">
    <div class="page-header">
      <h1 class="page-title">⚡ 策略生成</h1>
      <p class="page-description">基于防火墙路径计算，自动生成策略脚本</p>
    </div>

    <div class="grid grid-2">
      <div class="card">
        <h3 class="card-title">📝 策略配置</h3>
        <form @submit.prevent="generatePolicy">
          <div class="form-group">
            <label class="form-label">策略名称 *</label>
            <input
              v-model="form.policy_name"
              type="text"
              class="form-input"
              placeholder="例如：web_https_access"
              required
            />
          </div>

          <div class="grid grid-2">
            <div class="form-group">
              <label class="form-label">源地址 *</label>
              <div class="group-selector" @click.stop>
                <div class="selector-input-wrapper">
                  <input
                    v-model="sourceGroupName"
                    type="text"
                    class="form-input"
                    placeholder="选择或搜索地址组..."
                    readonly
                    @mousedown.prevent="toggleSourceDropdown"
                  />
                  <button
                    type="button"
                    class="btn-add"
                    @click="goToCreateAddressGroup"
                    title="创建新地址组"
                  >
                    +
                  </button>
                </div>
                <div v-if="showSourceDropdown" class="dropdown-panel" @click.stop>
                  <input
                    v-model="sourceSearch"
                    type="text"
                    class="form-input"
                    placeholder="搜索地址组..."
                  />
                  <div class="dropdown-list">
                    <div
                      v-for="group in filteredSourceGroups"
                      :key="group.id"
                      class="dropdown-item"
                      @click="selectSourceGroup(group)"
                    >
                      <div class="group-name">{{ group.name }}</div>
                      <div class="group-info">
                        {{ group.addresses?.length || 0 }} 个地址
                      </div>
                    </div>
                    <div v-if="filteredSourceGroups.length === 0" class="dropdown-empty">
                      <p>未找到地址组</p>
                      <button type="button" class="btn btn-sm btn-primary" @click="goToCreateAddressGroup">
                        + 创建新地址组
                      </button>
                    </div>
                  </div>
                </div>
                <div v-if="sourceGroupName" class="selected-info">
                  已选: {{ sourceGroupName }}
                  <span class="addr-count">({{ selectedSourceAddresses.length }} 个IP)</span>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">目的地址 *</label>
              <div class="group-selector" @click.stop>
                <div class="selector-input-wrapper">
                  <input
                    v-model="destGroupName"
                    type="text"
                    class="form-input"
                    placeholder="选择或搜索地址组..."
                    readonly
                    @mousedown.prevent="toggleDestDropdown"
                  />
                  <button
                    type="button"
                    class="btn-add"
                    @click="goToCreateAddressGroup"
                    title="创建新地址组"
                  >
                    +
                  </button>
                </div>
                <div v-if="showDestDropdown" class="dropdown-panel" @click.stop>
                  <input
                    v-model="destSearch"
                    type="text"
                    class="form-input"
                    placeholder="搜索地址组..."
                  />
                  <div class="dropdown-list">
                    <div
                      v-for="group in filteredDestGroups"
                      :key="group.id"
                      class="dropdown-item"
                      @click="selectDestGroup(group)"
                    >
                      <div class="group-name">{{ group.name }}</div>
                      <div class="group-info">
                        {{ group.addresses?.length || 0 }} 个地址
                      </div>
                    </div>
                    <div v-if="filteredDestGroups.length === 0" class="dropdown-empty">
                      <p>未找到地址组</p>
                      <button type="button" class="btn btn-sm btn-primary" @click="goToCreateAddressGroup">
                        + 创建新地址组
                      </button>
                    </div>
                  </div>
                </div>
                <div v-if="destGroupName" class="selected-info">
                  已选: {{ destGroupName }}
                  <span class="addr-count">({{ selectedDestAddresses.length }} 个IP)</span>
                </div>
              </div>
            </div>

          <div class="form-group">
              <label class="form-label">目标端口 *</label>
              <div class="group-selector" @click.stop>
                <div class="selector-input-wrapper">
                  <input
                    v-model="portGroupName"
                    type="text"
                    class="form-input"
                    placeholder="选择或搜索端口组..."
                    readonly
                    @mousedown.prevent="togglePortDropdown"
                  />
                  <button
                    type="button"
                    class="btn-add"
                    @click="goToCreatePortGroup"
                    title="创建新端口组"
                  >
                    +
                  </button>
                </div>
                <div v-if="showPortDropdown" class="dropdown-panel" @click.stop>
                  <input
                    v-model="portSearch"
                    type="text"
                    class="form-input"
                    placeholder="搜索端口组..."
                  />
                  <div class="dropdown-list">
                    <div
                      v-for="group in filteredPortGroups"
                      :key="group.id"
                      class="dropdown-item"
                      @click="selectPortGroup(group)"
                    >
                      <div class="group-name">{{ group.name }}</div>
                      <div class="group-info">
                        {{ group.ports?.length || 0 }} 个端口 ({{ group.protocol?.toUpperCase() }})
                      </div>
                    </div>
                    <div v-if="filteredPortGroups.length === 0" class="dropdown-empty">
                      <p>未找到端口组</p>
                      <button type="button" class="btn btn-sm btn-primary" @click="goToCreatePortGroup">
                        + 创建新端口组
                      </button>
                    </div>
                  </div>
                </div>
                <div v-if="portGroupName" class="selected-info">
                  已选: {{ portGroupName }}
                  <span class="addr-count">({{ selectedPorts.length }} 个端口)</span>
                </div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">描述</label>
            <input
              v-model="form.description"
              type="text"
              class="form-input"
              placeholder="可选的策略描述"
            />
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="generating || !isFormValid">
              {{ generating ? '生成中...' : '⚡ 生成策略' }}
            </button>
            <button type="button" class="btn" @click="resetForm" style="background: #999; color: white;">
              🔄 重置
            </button>
          </div>
        </form>

        <div v-if="message" :class="['message', message.type]">
          {{ message.text }}
        </div>
      </div>

      <div class="card">
        <h3 class="card-title">🛤️ 防火墙路径及Zone配置</h3>
        <div v-if="!generatedData.firewall_policies?.length" class="empty-state">
          <p>配置左侧表单后点击"生成策略"查看防火墙路径</p>
        </div>
        <div v-else class="path-preview">
          <div class="path-summary mb-4">
            <strong>路径摘要：</strong>{{ generatedData.path_summary }}
          </div>

          <div v-if="generatedData.path_group_details?.length > 1" class="path-groups">
            <div
              v-for="(pg, pgIndex) in generatedData.path_group_details"
              :key="pgIndex"
              class="path-group"
            >
              <div class="path-group-header">
                <span class="path-group-badge">路径 {{ pgIndex + 1 }}</span>
                <span class="path-group-desc">{{ pg.path_description }}</span>
                <span class="path-group-ips">
                  ({{ pg.source_ips?.join(', ') }} → {{ pg.dest_ips?.join(', ') }})
                </span>
              </div>
              <div class="path-group-firewalls">
                <span
                  v-for="(fw, fwIndex) in pg.policies"
                  :key="fwIndex"
                  class="path-fw-item"
                >
                  <span class="fw-name">{{ fw.device_name }}</span>
                  <span class="fw-zone">{{ fw.source_zone }} → {{ fw.dest_zone }}</span>
                  <span v-if="fwIndex < pg.policies.length - 1" class="path-separator"> -- </span>
                </span>
              </div>
            </div>
          </div>

          <div v-else class="path-single">
            <div
              v-for="(fw, index) in generatedData.firewall_policies"
              :key="index"
              class="path-item"
            >
              <div class="path-step">
                <div class="step-number">
                  {{ index + 1 }}
                  <div class="step-direction">{{ fw.flow_direction }}</div>
                </div>
                <div class="step-content">
                  <div class="device-info">
                    <span class="vendor-icon">{{ getVendorIcon(fw.device_name) }}</span>
                    <strong>{{ fw.device_name }}</strong>
                    <span class="badge" :class="getVendorBadge(fw.vendor)">{{ fw.vendor.toUpperCase() }}</span>
                  </div>
                  <div class="zone-details">
                    <div class="zone-item">
                      <span class="zone-label">源Zone:</span>
                      <span class="zone-name">{{ fw.source_zone }}</span>
                    </div>
                    <div class="zone-arrow">↓</div>
                    <div class="zone-item">
                      <span class="zone-label">目的Zone:</span>
                      <span class="zone-name">{{ fw.dest_zone }}</span>
                    </div>
                  </div>
                  <div class="ip-info">
                    <span>源IP: {{ sourceGroupName }}</span>
                    <span>→</span>
                    <span>目的IP: {{ destGroupName }}</span>
                  </div>
                </div>
              </div>
              <div v-if="index < generatedData.firewall_policies.length - 1" class="path-arrow">
                ↓ 流量经过
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="generatedData.firewall_policies?.length" class="card mt-4">
      <div class="flex flex-between mb-4">
        <h3 class="card-title">📄 生成的策略脚本</h3>
        <div>
          <button class="btn btn-primary" @click="copyAllScripts">
            📋 复制所有脚本
          </button>
        </div>
      </div>

      <div
        v-for="(fw, index) in generatedData.firewall_policies"
        :key="index"
        class="policy-script-item"
      >
        <div class="script-header">
          <h4>
            <span class="vendor-icon">{{ getVendorIcon(fw.device_name) }}</span>
            {{ fw.device_name }}
          </h4>
          <div class="script-actions">
            <button class="btn btn-primary" @click="copyScript(fw.policy_script, fw.device_name)">
              📋 复制
            </button>
            <button
              class="btn btn-success"
              @click="applyPolicy(fw)"
              :disabled="applying === fw.device_name"
            >
              {{ applying === fw.device_name ? '应用中...' : '🚀 应用到防火墙' }}
            </button>
          </div>
        </div>
        <div class="script-body">
          <pre class="code-block">{{ fw.policy_script }}</pre>
        </div>
      </div>
    </div>

    <div v-if="showApplyModal" class="modal-overlay" @click="showApplyModal = false">
      <div class="modal-content" @click.stop>
        <h3>🚀 应用结果</h3>
        <div class="modal-body">
          <div v-if="applyResult.loading" class="loading">应用策略中...</div>
          <div v-else-if="applyResult.error" class="error-message">
            {{ applyResult.error }}
          </div>
          <div v-else>
            <div class="result-item">
              <strong>状态：</strong>
              <span :class="['badge', applyResult.status === 'success' ? 'badge-success' : 'badge-error']">
                {{ applyResult.status }}
              </span>
            </div>
            <div class="result-item">
              <strong>设备：</strong>
              <span>{{ applyResult.device_name }}</span>
            </div>
            <div class="result-item">
              <strong>消息：</strong>
              <span>{{ applyResult.message }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary" @click="showApplyModal = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { policyAPI, addressGroupAPI, portGroupAPI } from '../services/api'

const router = useRouter()

const form = ref({
  policy_name: '',
  description: ''
})

const generating = ref(false)
const applying = ref('')
const generatedData = ref({})
const message = ref('')
const showApplyModal = ref(false)
const applyResult = ref({})

const addressGroups = ref([])
const portGroups = ref([])

const sourceGroupName = ref('')
const destGroupName = ref('')
const portGroupName = ref('')
const sourceSearch = ref('')
const destSearch = ref('')
const portSearch = ref('')
const showSourceDropdown = ref(false)
const showDestDropdown = ref(false)
const showPortDropdown = ref(false)

const selectedSourceAddresses = computed(() => {
  const group = addressGroups.value.find(g => g.name === sourceGroupName.value)
  return group?.addresses || []
})

const selectedDestAddresses = computed(() => {
  const group = addressGroups.value.find(g => g.name === destGroupName.value)
  return group?.addresses || []
})

const selectedPorts = computed(() => {
  const group = portGroups.value.find(g => g.name === portGroupName.value)
  return group?.ports || []
})

const filteredSourceGroups = computed(() => {
  if (!sourceSearch.value) return addressGroups.value
  const search = sourceSearch.value.toLowerCase()
  return addressGroups.value.filter(g => g.name.toLowerCase().includes(search))
})

const filteredDestGroups = computed(() => {
  if (!destSearch.value) return addressGroups.value
  const search = destSearch.value.toLowerCase()
  return addressGroups.value.filter(g => g.name.toLowerCase().includes(search))
})

const filteredPortGroups = computed(() => {
  if (!portSearch.value) return portGroups.value
  const search = portSearch.value.toLowerCase()
  return portGroups.value.filter(g => g.name.toLowerCase().includes(search))
})

const isFormValid = computed(() => {
  return sourceGroupName.value && destGroupName.value && portGroupName.value && form.value.policy_name
})

const loadGroups = async () => {
  try {
    const [addrResponse, portResponse] = await Promise.all([
      addressGroupAPI.getAll(),
      portGroupAPI.getAll()
    ])
    addressGroups.value = addrResponse.data.groups || []
    portGroups.value = portResponse.data.groups || []
  } catch (err) {
    console.error('加载组失败:', err)
  }
}

const selectSourceGroup = (group) => {
  sourceGroupName.value = group.name
  showSourceDropdown.value = false
  sourceSearch.value = ''
}

const selectDestGroup = (group) => {
  destGroupName.value = group.name
  showDestDropdown.value = false
  destSearch.value = ''
}

const selectPortGroup = (group) => {
  portGroupName.value = group.name
  showPortDropdown.value = false
  portSearch.value = ''
}

const toggleSourceDropdown = () => {
  showSourceDropdown.value = !showSourceDropdown.value
}

const toggleDestDropdown = () => {
  showDestDropdown.value = !showDestDropdown.value
}

const togglePortDropdown = () => {
  showPortDropdown.value = !showPortDropdown.value
}

const goToCreateAddressGroup = () => {
  router.push('/groups/address/create')
}

const goToCreatePortGroup = () => {
  router.push('/groups/port/create')
}

const generatePolicy = async () => {
  if (!isFormValid.value) {
    alert('请选择源地址组、目的地址组和端口组')
    return
  }

  generating.value = true
  message.value = ''

  try {
    const requestData = {
      policy_name: form.value.policy_name,
      source_group: sourceGroupName.value,
      dest_group: destGroupName.value,
      port_group: portGroupName.value,
      description: form.value.description
    }

    const response = await policyAPI.generate(requestData)
    generatedData.value = response.data.data || {}
    message.value = {
      type: 'success',
      text: `✅ 策略生成成功！共 ${generatedData.value.firewall_count} 台防火墙需要配置`
    }
  } catch (error) {
    message.value = {
      type: 'error',
      text: '❌ 生成失败：' + (error.response?.data?.detail || error.message)
    }
    console.error('生成策略失败:', error)
  } finally {
    generating.value = false
  }
}

const applyPolicy = async (fwPolicy) => {
  applying.value = fwPolicy.device_name
  applyResult.value = { loading: true }
  showApplyModal.value = true

  try {
    const response = await policyAPI.apply({
      device_name: fwPolicy.device_name,
      policy_script: fwPolicy.policy_script
    })
    applyResult.value = response.data
  } catch (error) {
    applyResult.value = {
      error: '应用失败：' + (error.response?.data?.detail || error.message)
    }
    console.error('应用策略失败:', error)
  } finally {
    applying.value = ''
  }
}

const copyScript = (script, deviceName) => {
  navigator.clipboard.writeText(script)
    .then(() => {
      alert(`✅ ${deviceName} 的策略脚本已复制到剪贴板`)
    })
    .catch(err => {
      console.error('复制失败:', err)
      alert('复制失败，请手动复制')
    })
}

const copyAllScripts = () => {
  const allScripts = generatedData.value.firewall_policies
    .map(fw => `=== ${fw.device_name} ===\n${fw.policy_script}`)
    .join('\n\n')

  navigator.clipboard.writeText(allScripts)
    .then(() => {
      alert('✅ 所有策略脚本已复制到剪贴板')
    })
    .catch(err => {
      console.error('复制失败:', err)
    })
}

const getVendorIcon = (deviceName) => {
  if (deviceName.includes('huawei')) return '🔵'
  if (deviceName.includes('hillstone')) return '🟠'
  if (deviceName.includes('h3c')) return '🟢'
  if (deviceName.includes('juniper')) return '🔴'
  return '🖥️'
}

const getVendorBadge = (vendor) => {
  const badges = {
    'huawei': 'vendor-huawei',
    'hillstone': 'vendor-hillstone',
    'h3c': 'vendor-h3c',
    'juniper': 'vendor-juniper'
  }
  return badges[vendor] || ''
}

const resetForm = () => {
  form.value = {
    policy_name: '',
    description: ''
  }
  sourceGroupName.value = ''
  destGroupName.value = ''
  portGroupName.value = ''
  generatedData.value = {}
  message.value = ''
}

const STORAGE_KEY = 'policy_generator_form'

const saveFormData = () => {
  const data = {
    policy_name: form.value.policy_name,
    description: form.value.description,
    sourceGroupName: sourceGroupName.value,
    destGroupName: destGroupName.value,
    portGroupName: portGroupName.value,
    generatedData: generatedData.value
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

const loadFormData = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const data = JSON.parse(saved)
      form.value.policy_name = data.policy_name || ''
      form.value.description = data.description || ''
      sourceGroupName.value = data.sourceGroupName || ''
      destGroupName.value = data.destGroupName || ''
      portGroupName.value = data.portGroupName || ''
      generatedData.value = data.generatedData || {}
    }
  } catch (err) {
    console.error('加载保存的表单数据失败:', err)
  }
}

watch([form, sourceGroupName, destGroupName, portGroupName, generatedData], () => {
  saveFormData()
}, { deep: true })

onMounted(() => {
  loadGroups()
  loadFormData()
  document.addEventListener('click', closeAllDropdowns)
})

const closeAllDropdowns = (event) => {
  const isInsideDropdown = event.target.closest('.group-selector')
  if (!isInsideDropdown) {
    showSourceDropdown.value = false
    showDestDropdown.value = false
    showPortDropdown.value = false
  }
}
</script>

<style scoped>
.form-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}

.message {
  margin-top: 16px;
  padding: 12px;
  border-radius: 6px;
}

.message.success {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}

.message.error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
}

.group-selector {
  position: relative;
}

.selector-input-wrapper {
  display: flex;
  gap: 4px;
}

.selector-input-wrapper .form-input {
  flex: 1;
}

.btn-add {
  width: 36px;
  height: 36px;
  background: #52c41a;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.btn-add:hover {
  background: #73d13d;
}

.dropdown-panel {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100;
  margin-top: 4px;
  max-height: 250px;
  overflow: hidden;
}

.dropdown-panel .form-input {
  border: none;
  border-bottom: 1px solid #f0f0f0;
  border-radius: 0;
}

.dropdown-list {
  max-height: 200px;
  overflow-y: auto;
}

.dropdown-item {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: #e6f7ff;
}

.group-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 2px;
}

.group-info {
  font-size: 12px;
  color: #999;
}

.dropdown-empty {
  padding: 16px;
  text-align: center;
  color: #999;
}

.dropdown-empty p {
  margin: 0 0 8px 0;
}

.selected-info {
  margin-top: 8px;
  font-size: 13px;
  color: #52c41a;
}

.addr-count {
  color: #999;
}

.path-preview {
  padding: 16px;
}

.path-summary {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  color: #1890ff;
}

.path-groups {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.path-group {
  border: 2px solid #d9d9d9;
  border-radius: 8px;
  overflow: hidden;
}

.path-group-header {
  background: #f5f5f5;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #d9d9d9;
}

.path-group-badge {
  background: #1890ff;
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.path-group-desc {
  font-weight: bold;
  color: #333;
}

.path-group-ips {
  color: #666;
  font-size: 13px;
}

.path-group-firewalls {
  padding: 12px 16px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  background: #fafafa;
}

.path-fw-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
}

.fw-name {
  font-weight: bold;
  color: #1890ff;
}

.fw-zone {
  font-size: 12px;
  color: #666;
}

.path-separator {
  color: #999;
  font-weight: bold;
  font-size: 16px;
}

.path-group-content {
  padding: 16px;
}

.path-single .path-item {
  margin-bottom: 16px;
}

.path-item {
  margin-bottom: 16px;
}

.path-step {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.step-number {
  width: 48px;
  height: 48px;
  background: #1890ff;
  color: white;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 18px;
  flex-shrink: 0;
}

.step-direction {
  font-size: 10px;
  font-weight: normal;
  margin-top: 2px;
}

.step-content {
  flex: 1;
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.device-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e8e8e8;
}

.device-info strong {
  font-size: 18px;
  color: #333;
}

.zone-details {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.zone-item {
  flex: 1;
  background: white;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
}

.zone-label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.zone-name {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 2px;
}

.zone-desc {
  font-size: 12px;
  color: #666;
}

.zone-arrow {
  font-size: 24px;
  color: #1890ff;
  font-weight: bold;
}

.ip-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
  background: white;
  padding: 8px 12px;
  border-radius: 4px;
}

.path-arrow {
  text-align: center;
  font-size: 16px;
  color: #52c41a;
  margin: 12px 0;
  padding: 8px;
  background: #f6ffed;
  border-radius: 4px;
  font-weight: 500;
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

.policy-script-item {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
}

.script-header {
  background: #f5f7fa;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.script-header h4 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.vendor-icon {
  font-size: 24px;
}

.script-actions {
  display: flex;
  gap: 8px;
}

.script-body {
  padding: 16px;
  background: white;
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

.modal-footer {
  text-align: right;
  margin-top: 20px;
}
</style>
