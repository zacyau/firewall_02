<template>
  <div class="space-y-6">
    <div>
      <h1 class="page-title">策略生成</h1>
      <p class="page-desc">基于防火墙路径计算，自动生成策略脚本</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card">
        <div class="card-header"><h3 class="text-sm font-semibold text-gray-900">策略配置</h3></div>
        <div class="card-body">
          <form @submit.prevent="generatePolicy" class="space-y-4">
            <div>
              <label class="form-label">策略名称 *</label>
              <input v-model="form.policy_name" type="text" class="form-input" placeholder="例如：web_https_access" required />
            </div>

            <div>
              <label class="form-label">源地址 *</label>
              <div class="relative" @click.stop>
                <div class="flex gap-1.5">
                  <input :value="sourceGroupName" type="text" class="form-input flex-1" placeholder="选择地址组..." readonly @mousedown.prevent="showSourceDropdown = !showSourceDropdown" />
                  <button type="button" class="btn-default btn-sm" @click="goToCreateAddressGroup">+</button>
                </div>
                <div v-if="showSourceDropdown" class="absolute z-20 left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-modal py-1 max-h-48 overflow-y-auto">
                  <input v-model="sourceSearch" type="text" class="form-input mx-2 mt-1 mb-1" placeholder="搜索..." style="width:calc(100% - 16px)" />
                  <div v-for="group in filteredSourceGroups" :key="group.id" class="px-3 py-2 hover:bg-gray-50 cursor-pointer text-sm" @click="selectSourceGroup(group)">
                    <span class="font-medium text-gray-900">{{ group.name }}</span>
                    <span class="text-xs text-gray-400 ml-2">{{ group.addresses?.length || 0 }} 个地址</span>
                  </div>
                  <div v-if="filteredSourceGroups.length === 0" class="px-3 py-3 text-xs text-gray-400 text-center">未找到地址组</div>
                </div>
                <div v-if="sourceGroupName" class="mt-1 text-xs text-gray-400">已选: {{ sourceGroupName }} ({{ selectedSourceAddresses.length }} 个IP)</div>
              </div>
            </div>

            <div>
              <label class="form-label">目的地址 *</label>
              <div class="relative" @click.stop>
                <div class="flex gap-1.5">
                  <input :value="destGroupName" type="text" class="form-input flex-1" placeholder="选择地址组..." readonly @mousedown.prevent="showDestDropdown = !showDestDropdown" />
                  <button type="button" class="btn-default btn-sm" @click="goToCreateAddressGroup">+</button>
                </div>
                <div v-if="showDestDropdown" class="absolute z-20 left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-modal py-1 max-h-48 overflow-y-auto">
                  <input v-model="destSearch" type="text" class="form-input mx-2 mt-1 mb-1" placeholder="搜索..." style="width:calc(100% - 16px)" />
                  <div v-for="group in filteredDestGroups" :key="group.id" class="px-3 py-2 hover:bg-gray-50 cursor-pointer text-sm" @click="selectDestGroup(group)">
                    <span class="font-medium text-gray-900">{{ group.name }}</span>
                    <span class="text-xs text-gray-400 ml-2">{{ group.addresses?.length || 0 }} 个地址</span>
                  </div>
                  <div v-if="filteredDestGroups.length === 0" class="px-3 py-3 text-xs text-gray-400 text-center">未找到地址组</div>
                </div>
                <div v-if="destGroupName" class="mt-1 text-xs text-gray-400">已选: {{ destGroupName }} ({{ selectedDestAddresses.length }} 个IP)</div>
              </div>
            </div>

            <div>
              <label class="form-label">目标端口 *</label>
              <div class="relative" @click.stop>
                <div class="flex gap-1.5">
                  <input :value="portGroupName" type="text" class="form-input flex-1" placeholder="选择端口组..." readonly @mousedown.prevent="showPortDropdown = !showPortDropdown" />
                  <button type="button" class="btn-default btn-sm" @click="goToCreatePortGroup">+</button>
                </div>
                <div v-if="showPortDropdown" class="absolute z-20 left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-modal py-1 max-h-48 overflow-y-auto">
                  <input v-model="portSearch" type="text" class="form-input mx-2 mt-1 mb-1" placeholder="搜索..." style="width:calc(100% - 16px)" />
                  <div v-for="group in filteredPortGroups" :key="group.id" class="px-3 py-2 hover:bg-gray-50 cursor-pointer text-sm" @click="selectPortGroup(group)">
                    <span class="font-medium text-gray-900">{{ group.name }}</span>
                    <span class="text-xs text-gray-400 ml-2">{{ group.ports?.length || 0 }} 个端口 ({{ group.protocol?.toUpperCase() }})</span>
                  </div>
                  <div v-if="filteredPortGroups.length === 0" class="px-3 py-3 text-xs text-gray-400 text-center">未找到端口组</div>
                </div>
                <div v-if="portGroupName" class="mt-1 text-xs text-gray-400">已选: {{ portGroupName }} ({{ selectedPorts.length }} 个端口)</div>
              </div>
            </div>

            <div>
              <label class="form-label">描述</label>
              <input v-model="form.description" type="text" class="form-input" placeholder="可选的策略描述" />
            </div>

            <div class="flex gap-3 pt-2">
              <button type="submit" class="btn-primary" :disabled="generating || !isFormValid">{{ generating ? '生成中...' : '生成策略' }}</button>
              <button type="button" class="btn-default" :disabled="generating || !isFormValid" @click="generatePolicyDryRun">{{ validating ? '验证中...' : '模拟验证' }}</button>
              <button type="button" class="btn-default" @click="resetForm">重置</button>
            </div>
          </form>

          <div v-if="message" :class="['mt-4 px-4 py-3 rounded-md text-sm', message.type === 'success' ? 'bg-success-50 text-success-700 border border-success-200' : 'bg-danger-50 text-danger-700 border border-danger-200']">
            {{ message.text }}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3 class="text-sm font-semibold text-gray-900">防火墙路径及Zone配置</h3></div>
        <div class="card-body">
          <div v-if="!generatedData.firewall_policies?.length" class="py-12 text-center text-sm text-gray-400">配置左侧表单后点击"生成策略"查看防火墙路径</div>
          <div v-else>
            <div class="mb-4 text-sm text-gray-600"><span class="font-medium">路径摘要：</span>{{ generatedData.path_summary }}</div>

            <div v-if="generatedData.path_group_details?.length > 1" class="space-y-6">
              <div v-for="(pg, pgIndex) in generatedData.path_group_details" :key="pgIndex">
                <div class="flex items-center gap-2 mb-3">
                  <span class="badge-primary">路径 {{ pgIndex + 1 }}</span>
                  <span class="text-xs text-gray-500">{{ pg.path_description }}</span>
                </div>
                <div class="space-y-3">
                  <div v-for="(fw, fwIndex) in pg.policies" :key="fwIndex" class="flex gap-3">
                    <div class="flex flex-col items-center">
                      <div class="w-7 h-7 rounded-full bg-primary-500 text-white flex items-center justify-center text-xs font-bold">{{ fwIndex + 1 }}</div>
                      <div v-if="fwIndex < pg.policies.length - 1" class="w-px flex-1 bg-gray-200 my-1"></div>
                    </div>
                    <div class="flex-1 pb-4">
                      <div class="flex items-center gap-2 mb-1">
                        <span class="text-sm font-medium text-gray-900">{{ fw.device_name }}</span>
                        <span :class="vendorBadge(fw.vendor)">{{ fw.vendor?.toUpperCase() }}</span>
                      </div>
                      <div class="text-xs text-gray-500 space-y-0.5">
                        <div>源Zone: <span class="font-medium text-gray-700">{{ fw.source_zone }}</span> → 目的Zone: <span class="font-medium text-gray-700">{{ fw.dest_zone }}</span></div>
                        <div>方向: {{ fw.flow_direction }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="space-y-3">
              <div v-for="(fw, index) in generatedData.firewall_policies" :key="index" class="flex gap-3">
                <div class="flex flex-col items-center">
                  <div class="w-7 h-7 rounded-full bg-primary-500 text-white flex items-center justify-center text-xs font-bold">{{ index + 1 }}</div>
                  <div v-if="index < generatedData.firewall_policies.length - 1" class="w-px flex-1 bg-gray-200 my-1"></div>
                </div>
                <div class="flex-1 pb-4">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-sm font-medium text-gray-900">{{ fw.device_name }}</span>
                    <span :class="vendorBadge(fw.vendor)">{{ fw.vendor?.toUpperCase() }}</span>
                  </div>
                  <div class="text-xs text-gray-500 space-y-0.5">
                    <div>源Zone: <span class="font-medium text-gray-700">{{ fw.source_zone }}</span> → 目的Zone: <span class="font-medium text-gray-700">{{ fw.dest_zone }}</span></div>
                    <div>方向: {{ fw.flow_direction }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="validationReport" class="card">
      <div class="card-header flex items-center justify-between">
        <div class="flex items-center gap-2">
          <h3 class="text-sm font-semibold text-gray-900">策略验证报告</h3>
          <span v-if="validationReport.valid" class="badge-success">通过</span>
          <span v-else class="badge-danger">未通过</span>
        </div>
        <button class="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100" @click="validationReport = null">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="card-body">
        <div class="mb-4 text-sm text-gray-600">{{ validationReport.summary }}</div>

        <div v-if="validationReport.issues?.length" class="space-y-2">
          <div v-for="(issue, idx) in validationReport.issues" :key="idx"
               :class="['flex items-start gap-3 px-4 py-3 rounded-lg border', issue.severity === 'error' ? 'bg-danger-50 border-danger-200' : 'bg-warning-50 border-warning-200']">
            <div class="shrink-0 mt-0.5">
              <svg v-if="issue.severity === 'error'" class="w-4 h-4 text-danger-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
              <svg v-else class="w-4 h-4 text-warning-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-0.5">
                <span :class="['text-xs font-medium px-1.5 py-0.5 rounded', issue.severity === 'error' ? 'bg-danger-100 text-danger-700' : 'bg-warning-100 text-warning-700']">
                  {{ issue.type === 'conflict' ? '冲突' : '冗余' }}
                </span>
                <span class="text-xs text-gray-500">规则 #{{ issue.rule_index + 1 }}</span>
                <span v-if="issue.existing_rule_id" class="text-xs text-gray-400">已有规则ID: {{ issue.existing_rule_id }}</span>
              </div>
              <div class="text-sm text-gray-700">{{ issue.desc }}</div>
            </div>
          </div>
        </div>

        <div v-if="validationReport.device_reports && Object.keys(validationReport.device_reports).length > 1" class="mt-4 border-t border-gray-200 pt-4">
          <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">各设备验证详情</h4>
          <div class="space-y-3">
            <div v-for="(report, deviceName) in validationReport.device_reports" :key="deviceName" class="border border-gray-200 rounded-lg px-4 py-3">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-sm font-medium text-gray-900">{{ deviceName }}</span>
                <span v-if="report.valid" class="badge-success text-xs">通过</span>
                <span v-else class="badge-danger text-xs">未通过</span>
              </div>
              <div class="text-xs text-gray-500">{{ report.summary }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="generatedData.firewall_policies?.length" class="card">
      <div class="card-header flex items-center justify-between">
        <h3 class="text-sm font-semibold text-gray-900">生成的策略脚本</h3>
        <div class="flex items-center gap-2">
          <label class="flex items-center gap-1.5 text-xs text-gray-600 cursor-pointer">
            <input v-model="simulateMode" type="checkbox" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
            模拟模式（无真实设备）
          </label>
          <button class="btn-default btn-sm" @click="copyAllScripts">复制所有脚本</button>
        </div>
      </div>
      <div class="card-body space-y-4">
        <div v-for="(fw, index) in generatedData.firewall_policies" :key="index" class="border border-gray-200 rounded-lg overflow-hidden">
          <div class="flex items-center justify-between px-4 py-2.5 bg-gray-50 border-b border-gray-200">
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium text-gray-900">{{ fw.device_name }}</span>
              <span :class="vendorBadge(fw.vendor)">{{ fw.vendor?.toUpperCase() }}</span>
              <span v-if="fw.applyStatus" :class="statusBadge(fw.applyStatus)">{{ statusText(fw.applyStatus) }}</span>
            </div>
            <div class="flex items-center gap-2">
              <button class="btn-default btn-sm" @click="copyScript(fw.policy_script, fw.device_name)">复制</button>
              <button 
                :class="fw.applyStatus === 'failed' ? 'btn-warning btn-sm' : 'btn-primary btn-sm'" 
                @click="applyPolicy(fw)" 
                :disabled="applying === fw.device_name || fw.applyStatus === 'applied'"
              >
                {{ applying === fw.device_name ? '应用中...' : fw.applyStatus === 'failed' ? '重试' : fw.applyStatus === 'applied' ? '已应用' : '应用到防火墙' }}
              </button>
            </div>
          </div>
          <pre class="code-block m-0 rounded-none border-none">{{ fw.policy_script }}</pre>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showApplyModal" class="modal-backdrop" @click.self="showApplyModal = false">
        <div class="modal-panel" @click.stop>
          <div class="modal-header">
            <h3 class="text-base font-semibold text-gray-900">应用结果</h3>
            <button class="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100" @click="showApplyModal = false">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="applyResult.loading" class="text-center text-sm text-gray-400 py-4">应用策略中...</div>
            <div v-else-if="applyResult.error" class="text-sm text-danger-500">{{ applyResult.error }}</div>
            <div v-else class="space-y-2 text-sm">
              <div class="flex gap-2"><span class="text-gray-500 w-16 shrink-0">状态：</span><span :class="applyResult.status === 'success' ? 'badge-success' : 'badge-danger'">{{ applyResult.status }}</span></div>
              <div class="flex gap-2"><span class="text-gray-500 w-16 shrink-0">设备：</span><span>{{ applyResult.device_name }}</span></div>
              <div class="flex gap-2"><span class="text-gray-500 w-16 shrink-0">消息：</span><span>{{ applyResult.message }}</span></div>
              <div v-if="simulateMode && applyResult.status === 'success'" class="mt-2 p-2 bg-warning-50 border border-warning-200 rounded text-xs text-warning-700">
                当前为模拟模式，策略已保存到数据库但未下发到真实设备
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-default" @click="showApplyModal = false">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { policyAPI, addressGroupAPI, portGroupAPI } from '../services/api'

const router = useRouter()

// sessionStorage key
const STORAGE_KEY = 'policy_generator_form'

const form = ref({ policy_name: '', description: '' })
const generating = ref(false)
const validating = ref(false)
const applying = ref('')
const generatedData = ref({})
const message = ref('')
const showApplyModal = ref(false)
const applyResult = ref({})
const validationReport = ref(null)
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
const simulateMode = ref(true) // 默认模拟模式

// 保存表单数据到 sessionStorage
const saveFormToStorage = () => {
  const data = {
    form: form.value,
    sourceGroupName: sourceGroupName.value,
    destGroupName: destGroupName.value,
    portGroupName: portGroupName.value,
    simulateMode: simulateMode.value,
    timestamp: Date.now()
  }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

// 从 sessionStorage 恢复表单数据
const loadFormFromStorage = () => {
  try {
    const stored = sessionStorage.getItem(STORAGE_KEY)
    if (stored) {
      const data = JSON.parse(stored)
      // 恢复表单数据
      if (data.form) {
        form.value = { ...form.value, ...data.form }
      }
      if (data.sourceGroupName) {
        sourceGroupName.value = data.sourceGroupName
      }
      if (data.destGroupName) {
        destGroupName.value = data.destGroupName
      }
      if (data.portGroupName) {
        portGroupName.value = data.portGroupName
      }
      if (data.simulateMode !== undefined) {
        simulateMode.value = data.simulateMode
      }
      return true
    }
  } catch (e) {
    console.error('恢复表单数据失败:', e)
    sessionStorage.removeItem(STORAGE_KEY)
  }
  return false
}

// 清除 sessionStorage 中的表单数据
const clearFormStorage = () => {
  sessionStorage.removeItem(STORAGE_KEY)
}

// 监听表单数据变化，实时保存到 sessionStorage
watch(() => form.value, saveFormToStorage, { deep: true })
watch(sourceGroupName, saveFormToStorage)
watch(destGroupName, saveFormToStorage)
watch(portGroupName, saveFormToStorage)
watch(simulateMode, saveFormToStorage)

const selectedSourceAddresses = computed(() => addressGroups.value.find(g => g.name === sourceGroupName.value)?.addresses || [])
const selectedDestAddresses = computed(() => addressGroups.value.find(g => g.name === destGroupName.value)?.addresses || [])
const selectedPorts = computed(() => portGroups.value.find(g => g.name === portGroupName.value)?.ports || [])
const filteredSourceGroups = computed(() => { if (!sourceSearch.value) return addressGroups.value; return addressGroups.value.filter(g => g.name.toLowerCase().includes(sourceSearch.value.toLowerCase())) })
const filteredDestGroups = computed(() => { if (!destSearch.value) return addressGroups.value; return addressGroups.value.filter(g => g.name.toLowerCase().includes(destSearch.value.toLowerCase())) })
const filteredPortGroups = computed(() => { if (!portSearch.value) return portGroups.value; return portGroups.value.filter(g => g.name.toLowerCase().includes(portSearch.value.toLowerCase())) })
const isFormValid = computed(() => sourceGroupName.value && destGroupName.value && portGroupName.value && form.value.policy_name)
const vendorBadge = (v) => ({ huawei: 'badge-primary', hillstone: 'badge-warning', h3c: 'badge-success', juniper: 'badge-danger' }[v] || 'badge-gray')

const statusBadge = (status) => ({
  pending: 'badge-gray',
  applying: 'badge-blue',
  applied: 'badge-success',
  failed: 'badge-danger'
}[status] || 'badge-gray')

const statusText = (status) => ({
  pending: '待下发',
  applying: '下发中',
  applied: '已应用',
  failed: '失败'
}[status] || status)

const loadGroups = async () => {
  try {
    const [addrR, portR] = await Promise.all([addressGroupAPI.getAll(), portGroupAPI.getAll()])
    addressGroups.value = addrR.data.groups || []; portGroups.value = portR.data.groups || []
  } catch (e) { console.error('加载组失败:', e) }
}

const selectSourceGroup = (g) => { sourceGroupName.value = g.name; showSourceDropdown.value = false; sourceSearch.value = '' }
const selectDestGroup = (g) => { destGroupName.value = g.name; showDestDropdown.value = false; destSearch.value = '' }
const selectPortGroup = (g) => { portGroupName.value = g.name; showPortDropdown.value = false; portSearch.value = '' }
const goToCreateAddressGroup = () => router.push('/groups/address/create')
const goToCreatePortGroup = () => router.push('/groups/port/create')

const generatePolicy = async () => {
  if (!isFormValid.value) return
  generating.value = true; message.value = ''; validationReport.value = null
  try {
    const r = await policyAPI.generate({ policy_name: form.value.policy_name, source_group: sourceGroupName.value, dest_group: destGroupName.value, port_group: portGroupName.value, description: form.value.description })
    generatedData.value = r.data.data || {}
    message.value = { type: 'success', text: `策略生成成功！共 ${generatedData.value.firewall_count} 台防火墙需要配置` }
  } catch (e) { message.value = { type: 'error', text: '生成失败：' + (e.response?.data?.detail || e.message) } }
  finally { generating.value = false }
}

const generatePolicyDryRun = async () => {
  if (!isFormValid.value) return
  validating.value = true; message.value = ''; validationReport.value = null
  try {
    const r = await policyAPI.generateDryRun({ policy_name: form.value.policy_name, source_group: sourceGroupName.value, dest_group: destGroupName.value, port_group: portGroupName.value, description: form.value.description })
    generatedData.value = r.data.data || {}
    const validation = r.data.data.validation
    if (validation) {
      validationReport.value = validation
      const conflictCount = validation.issues?.filter(i => i.type === 'conflict').length || 0
      const redundancyCount = validation.issues?.filter(i => i.type === 'redundancy').length || 0
      if (validation.valid) {
        message.value = { type: 'success', text: `模拟验证完成：无冲突${redundancyCount > 0 ? `，发现 ${redundancyCount} 个冗余规则` : ''}` }
      } else {
        message.value = { type: 'error', text: `模拟验证发现 ${conflictCount} 个冲突${redundancyCount > 0 ? `，${redundancyCount} 个冗余规则` : ''}，请查看验证报告` }
      }
    } else {
      message.value = { type: 'success', text: `策略生成成功！共 ${generatedData.value.firewall_count} 台防火墙需要配置` }
    }
  } catch (e) { message.value = { type: 'error', text: '验证失败：' + (e.response?.data?.detail || e.message) } }
  finally { validating.value = false }
}

const applyPolicy = async (fwPolicy) => {
  applying.value = fwPolicy.device_name
  applyResult.value = { loading: true }
  showApplyModal.value = true
  
  // 设置状态为 applying
  fwPolicy.applyStatus = 'applying'
  
  try {
    const r = await policyAPI.apply({
      policy_name: form.value.policy_name,
      device_name: fwPolicy.device_name,
      policy_script: fwPolicy.policy_script,
      source_ip: sourceGroupName.value,
      dest_ip: destGroupName.value,
      protocol: portGroups.value.find(g => g.name === portGroupName.value)?.protocol || 'tcp',
      dest_port: portGroupName.value,
      source_zone: fwPolicy.source_zone,
      dest_zone: fwPolicy.dest_zone,
      action: 'permit'
    }, simulateMode.value)
    
    applyResult.value = r.data
    
    // 根据结果更新状态
    if (r.data.status === 'success') {
      fwPolicy.applyStatus = 'applied'
      fwPolicy.policyId = r.data.policy_id
    } else {
      fwPolicy.applyStatus = 'failed'
      fwPolicy.errorMessage = r.data.message
    }
  } catch (e) {
    applyResult.value = { error: '应用失败：' + (e.response?.data?.detail || e.message) }
    fwPolicy.applyStatus = 'failed'
    fwPolicy.errorMessage = e.response?.data?.detail || e.message
  } finally {
    applying.value = ''
  }
}

const copyScript = (script, name) => { navigator.clipboard.writeText(script).then(() => alert(`${name} 的策略脚本已复制`)).catch(() => alert('复制失败')) }
const copyAllScripts = () => { const s = generatedData.value.firewall_policies.map(fw => `=== ${fw.device_name} ===\n${fw.policy_script}`).join('\n\n'); navigator.clipboard.writeText(s).then(() => alert('所有脚本已复制')).catch(() => {}) }

const resetForm = () => {
  form.value = { policy_name: '', description: '' }
  sourceGroupName.value = ''
  destGroupName.value = ''
  portGroupName.value = ''
  generatedData.value = {}
  message.value = ''
  validationReport.value = null
  clearFormStorage()
}

const closeAllDropdowns = (e) => { if (!e.target.closest('.relative')) { showSourceDropdown.value = false; showDestDropdown.value = false; showPortDropdown.value = false } }

onMounted(() => {
  loadGroups()
  // 页面加载时从 sessionStorage 恢复数据
  const restored = loadFormFromStorage()
  if (restored) {
    message.value = { type: 'success', text: '已恢复之前的输入数据' }
    // 3秒后清除提示
    setTimeout(() => { if (message.value?.text === '已恢复之前的输入数据') message.value = '' }, 3000)
  }
  document.addEventListener('click', closeAllDropdowns)
})
onBeforeUnmount(() => { document.removeEventListener('click', closeAllDropdowns) })
</script>
