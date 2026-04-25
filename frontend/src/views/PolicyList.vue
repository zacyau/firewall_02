<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">策略管理</h1>
        <p class="page-desc">管理所有防火墙安全策略</p>
      </div>
      <router-link to="/policies/generate" class="btn-primary">生成新策略</router-link>
    </div>

    <div class="card">
      <div class="card-header flex items-center justify-between">
        <div class="flex items-center gap-3">
          <select v-model="filterStatus" class="form-select w-32 text-sm">
            <option value="">全部状态</option>
            <option value="pending">待应用</option>
            <option value="applied">已应用</option>
            <option value="failed">失败</option>
          </select>
        </div>
        <span class="text-xs text-gray-400">共 {{ filteredPolicies.length }} 条</span>
      </div>

      <div v-if="loading" class="py-12 text-center text-sm text-gray-400">加载中...</div>
      <div v-else-if="error" class="px-6 py-4 text-sm text-danger-500">{{ error }}</div>
      <div v-else-if="filteredPolicies.length === 0" class="empty-state py-16">
        <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>
        <p class="text-sm text-gray-400 mb-3">暂无策略</p>
        <router-link to="/policies/generate" class="btn-primary btn-sm">生成策略</router-link>
      </div>

      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>策略名称</th>
              <th>源IP</th>
              <th>目标IP</th>
              <th>协议</th>
              <th>端口</th>
              <th>源区域</th>
              <th>目标区域</th>
              <th>设备</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="policy in filteredPolicies" :key="policy.id">
              <td class="text-gray-400">{{ policy.id }}</td>
              <td class="font-medium text-gray-900">{{ policy.policy_name }}</td>
              <td class="font-mono text-xs">{{ policy.source_ip }}</td>
              <td class="font-mono text-xs">{{ policy.dest_ip }}</td>
              <td><span class="badge-gray">{{ policy.protocol?.toUpperCase() }}</span></td>
              <td class="font-mono text-xs">{{ policy.dest_port }}</td>
              <td>{{ policy.source_zone || '-' }}</td>
              <td>{{ policy.dest_zone || '-' }}</td>
              <td>{{ policy.device_name || '-' }}</td>
              <td><span :class="statusBadge(policy.status)">{{ statusText(policy.status) }}</span></td>
              <td class="text-xs text-gray-400">{{ formatTime(policy.created_at) }}</td>
              <td>
                <button class="btn-default btn-sm" @click="viewDetails(policy)">查看</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showDetailModal" class="modal-backdrop" @click.self="showDetailModal = false">
        <div class="modal-panel-lg" @click.stop>
          <div class="modal-header">
            <h3 class="text-base font-semibold text-gray-900">策略详情</h3>
            <button class="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100" @click="showDetailModal = false">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div v-if="selectedPolicy" class="modal-body space-y-4">
            <div class="grid grid-cols-2 gap-x-8 gap-y-3">
              <div v-for="item in detailFields" :key="item.label" class="flex items-center gap-2 text-sm">
                <span class="text-gray-500 shrink-0">{{ item.label }}：</span>
                <span v-if="item.isBadge" :class="statusBadge(selectedPolicy[item.key])">{{ statusText(selectedPolicy[item.key]) }}</span>
                <span v-else class="text-gray-900">{{ selectedPolicy[item.key] || '-' }}</span>
              </div>
            </div>
            <div v-if="selectedPolicy.policy_script">
              <div class="text-sm font-medium text-gray-700 mb-2">策略脚本</div>
              <pre class="code-block max-h-80 overflow-y-auto">{{ selectedPolicy.policy_script }}</pre>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-default" @click="showDetailModal = false">关闭</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { policyAPI } from '../services/api'

const policies = ref([])
const loading = ref(false)
const error = ref('')
const filterStatus = ref('')
const showDetailModal = ref(false)
const selectedPolicy = ref(null)

const filteredPolicies = computed(() => {
  if (!filterStatus.value) return policies.value
  return policies.value.filter(p => p.status === filterStatus.value)
})

const detailFields = [
  { label: '策略名称', key: 'policy_name' },
  { label: '状态', key: 'status', isBadge: true },
  { label: '源IP', key: 'source_ip' },
  { label: '目标IP', key: 'dest_ip' },
  { label: '协议', key: 'protocol' },
  { label: '端口', key: 'dest_port' },
  { label: '源区域', key: 'source_zone' },
  { label: '目标区域', key: 'dest_zone' },
  { label: '设备', key: 'device_name' },
  { label: '创建时间', key: 'created_at' },
]

const statusBadge = (s) => ({ applied: 'badge-success', pending: 'badge-warning', failed: 'badge-danger' }[s] || 'badge-gray')
const statusText = (s) => ({ applied: '已应用', pending: '待应用', failed: '失败' }[s] || s)
const formatTime = (t) => t ? new Date(t).toLocaleString('zh-CN') : '-'

const viewDetails = (policy) => { selectedPolicy.value = policy; showDetailModal.value = true }

onMounted(async () => {
  loading.value = true
  try {
    const res = await policyAPI.getAll()
    policies.value = res.data.policies || []
  } catch (err) {
    error.value = '加载策略列表失败：' + (err.message || '未知错误')
  } finally {
    loading.value = false
  }
})
</script>
