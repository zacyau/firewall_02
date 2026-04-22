<template>
  <div class="policy-list">
    <div class="page-header">
      <div class="flex flex-between">
        <div>
          <h1 class="page-title">📋 策略管理</h1>
          <p class="page-description">管理所有防火墙安全策略</p>
        </div>
        <router-link to="/policies/generate" class="btn btn-primary">
          ⚡ 生成新策略
        </router-link>
      </div>
    </div>

    <div class="card">
      <div class="filters">
        <select v-model="filterStatus" class="form-select" style="width: auto;">
          <option value="">全部状态</option>
          <option value="pending">待应用</option>
          <option value="applied">已应用</option>
          <option value="failed">失败</option>
        </select>
      </div>

      <div v-if="loading" class="loading">加载中...</div>
      
      <div v-else-if="error" class="error-message">{{ error }}</div>
      
      <div v-else-if="filteredPolicies.length === 0" class="empty-state">
        <div class="empty-state-icon">📋</div>
        <h3>暂无策略</h3>
        <p>点击下方按钮创建第一个策略</p>
        <router-link to="/policies/generate" class="btn btn-primary mt-4">
          生成策略
        </router-link>
      </div>

      <table v-else class="table">
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
            <td>{{ policy.id }}</td>
            <td><strong>{{ policy.policy_name }}</strong></td>
            <td>{{ policy.source_ip }}</td>
            <td>{{ policy.dest_ip }}</td>
            <td>{{ policy.protocol?.toUpperCase() }}</td>
            <td>{{ policy.dest_port }}</td>
            <td>{{ policy.source_zone || '-' }}</td>
            <td>{{ policy.dest_zone || '-' }}</td>
            <td>{{ policy.device_name || '-' }}</td>
            <td>
              <span :class="['badge', getStatusBadge(policy.status)]">
                {{ getStatusText(policy.status) }}
              </span>
            </td>
            <td>{{ formatTime(policy.created_at) }}</td>
            <td>
              <div class="action-buttons" style="flex-direction: column;">
                <button class="btn btn-primary" @click="viewDetails(policy)">
                  👁️ 查看
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 策略详情弹窗 -->
    <div v-if="showDetailModal" class="modal-overlay" @click="showDetailModal = false">
      <div class="modal-content modal-large" @click.stop>
        <h3>📋 策略详情</h3>
        <div class="modal-body">
          <div v-if="selectedPolicy" class="policy-details">
            <div class="detail-grid">
              <div class="detail-item">
                <strong>策略名称：</strong>
                <span>{{ selectedPolicy.policy_name }}</span>
              </div>
              <div class="detail-item">
                <strong>状态：</strong>
                <span :class="['badge', getStatusBadge(selectedPolicy.status)]">
                  {{ getStatusText(selectedPolicy.status) }}
                </span>
              </div>
              <div class="detail-item">
                <strong>源IP：</strong>
                <span>{{ selectedPolicy.source_ip }}</span>
              </div>
              <div class="detail-item">
                <strong>目标IP：</strong>
                <span>{{ selectedPolicy.dest_ip }}</span>
              </div>
              <div class="detail-item">
                <strong>协议：</strong>
                <span>{{ selectedPolicy.protocol?.toUpperCase() }}</span>
              </div>
              <div class="detail-item">
                <strong>端口：</strong>
                <span>{{ selectedPolicy.dest_port }}</span>
              </div>
              <div class="detail-item">
                <strong>源区域：</strong>
                <span>{{ selectedPolicy.source_zone || '-' }}</span>
              </div>
              <div class="detail-item">
                <strong>目标区域：</strong>
                <span>{{ selectedPolicy.dest_zone || '-' }}</span>
              </div>
              <div class="detail-item">
                <strong>设备：</strong>
                <span>{{ selectedPolicy.device_name || '-' }}</span>
              </div>
              <div class="detail-item">
                <strong>创建时间：</strong>
                <span>{{ formatTime(selectedPolicy.created_at) }}</span>
              </div>
            </div>

            <div v-if="selectedPolicy.policy_script" class="script-section">
              <h4>策略脚本</h4>
              <pre class="code-block">{{ selectedPolicy.policy_script }}</pre>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary" @click="showDetailModal = false">关闭</button>
        </div>
      </div>
    </div>
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

const loadPolicies = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await policyAPI.getAll()
    policies.value = response.data.policies || []
  } catch (err) {
    error.value = '加载策略列表失败：' + (err.message || '未知错误')
    console.error('加载策略失败:', err)
  } finally {
    loading.value = false
  }
}

const viewDetails = (policy) => {
  selectedPolicy.value = policy
  showDetailModal.value = true
}

const getStatusBadge = (status) => {
  const badges = {
    'applied': 'badge-success',
    'pending': 'badge-warning',
    'failed': 'badge-error'
  }
  return badges[status] || 'badge-info'
}

const getStatusText = (status) => {
  const texts = {
    'applied': '已应用',
    'pending': '待应用',
    'failed': '失败'
  }
  return texts[status] || status
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadPolicies()
})
</script>

<style scoped>
.filters {
  margin-bottom: 16px;
}

.policy-details {
  padding: 0;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.detail-item {
  padding: 8px 0;
  font-size: 14px;
}

.detail-item strong {
  color: #666;
  display: block;
  margin-bottom: 4px;
}

.script-section {
  margin-top: 24px;
}

.script-section h4 {
  margin-bottom: 12px;
  color: #333;
}

.modal-large {
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.action-buttons {
  display: flex;
  gap: 8px;
}
</style>
