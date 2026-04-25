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

    <div v-if="generatedData.firewall_policies?.length" class="card">
      <div class="card-header flex items-center justify-between">
        <h3 class="text-sm font-semibold text-gray-900">生成的策略脚本</h3>
        <button class="btn-default btn-sm" @click="copyAllScripts">复制所有脚本</button>
      </div>
      <div class="card-body space-y-4">
        <div v-for="(fw, index) in generatedData.firewall_policies" :key="index" class="border border-gray-200 rounded-lg overflow-hidden">
          <div class="flex items-center justify-between px-4 py-2.5 bg-gray-50 border-b border-gray-200">
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium text-gray-900">{{ fw.device_name }}</span>
              <span :class="vendorBadge(fw.vendor)">{{ fw.vendor?.toUpperCase() }}</span>
            </div>
            <div class="flex items-center gap-2">
              <button class="btn-default btn-sm" @click="copyScript(fw.policy_script, fw.device_name)">复制</button>
              <button class="btn-primary btn-sm" @click="applyPolicy(fw)" :disabled="applying === fw.device_name">
                {{ applying === fw.device_name ? '应用中...' : '应用到防火墙' }}
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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { policyAPI, addressGroupAPI, portGroupAPI } from '../services/api'

const router = useRouter()
const form = ref({ policy_name: '', description: '' })
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

const selectedSourceAddresses = computed(() => addressGroups.value.find(g => g.name === sourceGroupName.value)?.addresses || [])
const selectedDestAddresses = computed(() => addressGroups.value.find(g => g.name === destGroupName.value)?.addresses || [])
const selectedPorts = computed(() => portGroups.value.find(g => g.name === portGroupName.value)?.ports || [])
const filteredSourceGroups = computed(() => { if (!sourceSearch.value) return addressGroups.value; return addressGroups.value.filter(g => g.name.toLowerCase().includes(sourceSearch.value.toLowerCase())) })
const filteredDestGroups = computed(() => { if (!destSearch.value) return addressGroups.value; return addressGroups.value.filter(g => g.name.toLowerCase().includes(destSearch.value.toLowerCase())) })
const filteredPortGroups = computed(() => { if (!portSearch.value) return portGroups.value; return portGroups.value.filter(g => g.name.toLowerCase().includes(portSearch.value.toLowerCase())) })
const isFormValid = computed(() => sourceGroupName.value && destGroupName.value && portGroupName.value && form.value.policy_name)
const vendorBadge = (v) => ({ huawei: 'badge-primary', hillstone: 'badge-warning', h3c: 'badge-success', juniper: 'badge-danger' }[v] || 'badge-gray')

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
  generating.value = true; message.value = ''
  try {
    const r = await policyAPI.generate({ policy_name: form.value.policy_name, source_group: sourceGroupName.value, dest_group: destGroupName.value, port_group: portGroupName.value, description: form.value.description })
    generatedData.value = r.data.data || {}
    message.value = { type: 'success', text: `策略生成成功！共 ${generatedData.value.firewall_count} 台防火墙需要配置` }
  } catch (e) { message.value = { type: 'error', text: '生成失败：' + (e.response?.data?.detail || e.message) } }
  finally { generating.value = false }
}

const applyPolicy = async (fwPolicy) => {
  applying.value = fwPolicy.device_name; applyResult.value = { loading: true }; showApplyModal.value = true
  try { const r = await policyAPI.apply({ device_name: fwPolicy.device_name, policy_script: fwPolicy.policy_script }); applyResult.value = r.data }
  catch (e) { applyResult.value = { error: '应用失败：' + (e.response?.data?.detail || e.message) } }
  finally { applying.value = '' }
}

const copyScript = (script, name) => { navigator.clipboard.writeText(script).then(() => alert(`${name} 的策略脚本已复制`)).catch(() => alert('复制失败')) }
const copyAllScripts = () => { const s = generatedData.value.firewall_policies.map(fw => `=== ${fw.device_name} ===\n${fw.policy_script}`).join('\n\n'); navigator.clipboard.writeText(s).then(() => alert('所有脚本已复制')).catch(() => {}) }

const resetForm = () => { form.value = { policy_name: '', description: '' }; sourceGroupName.value = ''; destGroupName.value = ''; portGroupName.value = ''; generatedData.value = {}; message.value = '' }

const closeAllDropdowns = (e) => { if (!e.target.closest('.relative')) { showSourceDropdown.value = false; showDestDropdown.value = false; showPortDropdown.value = false } }

onMounted(() => { loadGroups(); document.addEventListener('click', closeAllDropdowns) })
onBeforeUnmount(() => { document.removeEventListener('click', closeAllDropdowns) })
</script>
