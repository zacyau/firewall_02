<template>
  <div class="dashboard">
    <div class="page-header">
      <h1 class="page-title">🏠 控制台</h1>
      <p class="page-description">防火墙自动化运维平台 - 多品牌统一管理</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">🖥️</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalDevices }}</div>
          <div class="stat-label">设备总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.onlineDevices }}</div>
          <div class="stat-label">在线设备</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📋</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalPolicies }}</div>
          <div class="stat-label">策略总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🔒</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.appliedPolicies }}</div>
          <div class="stat-label">已应用策略</div>
        </div>
      </div>
    </div>

    <div class="grid grid-2">
      <div class="card">
        <h3 class="card-title">🚀 快速开始</h3>
        <div class="quick-actions">
          <router-link to="/devices/register" class="quick-action-btn">
            <span>🖥️</span>
            <span>注册新设备</span>
          </router-link>
          <router-link to="/policies/generate" class="quick-action-btn">
            <span>⚡</span>
            <span>生成策略</span>
          </router-link>
          <router-link to="/devices" class="quick-action-btn">
            <span>📊</span>
            <span>查看设备</span>
          </router-link>
          <router-link to="/policies" class="quick-action-btn">
            <span>📋</span>
            <span>管理策略</span>
          </router-link>
        </div>
      </div>

      <div class="card">
        <h3 class="card-title">📖 平台特性</h3>
        <ul class="feature-list">
          <li>✓ 支持华为、山石、新华三、瞻博四大品牌防火墙</li>
          <li>✓ 统一适配层，自动适配不同厂商CLI命令</li>
          <li>✓ 智能路径计算，自动识别流量经过的防火墙</li>
          <li>✓ 策略模板库，基于Jinja2标准化生成</li>
          <li>✓ 审核流程，策略下发前人工确认</li>
          <li>✓ API接口，便于集成和自动化</li>
        </ul>
      </div>
    </div>

    <div class="card mt-4">
      <h3 class="card-title">📝 最新策略</h3>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="recentPolicies.length === 0" class="empty-state">
        <p>暂无策略记录</p>
        <router-link to="/policies/generate" class="btn btn-primary mt-4">
          创建第一个策略
        </router-link>
      </div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>策略名称</th>
            <th>源IP</th>
            <th>目标IP</th>
            <th>协议</th>
            <th>端口</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="policy in recentPolicies" :key="policy.id">
            <td>{{ policy.policy_name }}</td>
            <td>{{ policy.source_ip }}</td>
            <td>{{ policy.dest_ip }}</td>
            <td>{{ policy.protocol.toUpperCase() }}</td>
            <td>{{ policy.dest_port }}</td>
            <td>
              <span :class="['badge', getStatusBadge(policy.status)]">
                {{ policy.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { deviceAPI, policyAPI } from '../services/api'

const stats = ref({
  totalDevices: 0,
  onlineDevices: 0,
  totalPolicies: 0,
  appliedPolicies: 0
})

const recentPolicies = ref([])
const loading = ref(false)

const loadStats = async () => {
  try {
    const [devicesRes, policiesRes] = await Promise.all([
      deviceAPI.getAll(),
      policyAPI.getAll()
    ])

    stats.value.totalDevices = devicesRes.data.count || 0
    stats.value.onlineDevices = devicesRes.data.devices?.filter(d => d.status === 'online').length || 0
    stats.value.totalPolicies = policiesRes.data.count || 0
    stats.value.appliedPolicies = policiesRes.data.policies?.filter(p => p.status === 'applied').length || 0
    recentPolicies.value = policiesRes.data.policies?.slice(-5).reverse() || []
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const getStatusBadge = (status) => {
  const badges = {
    'applied': 'badge-success',
    'pending': 'badge-warning',
    'failed': 'badge-error'
  }
  return badges[status] || 'badge-info'
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  font-size: 48px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1890ff;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  font-weight: 500;
  transition: all 0.3s;
}

.quick-action-btn:hover {
  background: #1890ff;
  color: white;
  transform: translateX(4px);
}

.quick-action-btn span:first-child {
  font-size: 24px;
}

.feature-list {
  list-style: none;
  padding: 0;
}

.feature-list li {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

.feature-list li:last-child {
  border-bottom: none;
}
</style>
