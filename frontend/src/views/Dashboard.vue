<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card px-5 py-4">
        <div class="flex items-center gap-4">
          <div class="flex items-center justify-center w-10 h-10 rounded-lg bg-primary-50 text-primary-500">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ stats.totalDevices }}</div>
            <div class="text-xs text-gray-500">设备总数</div>
          </div>
        </div>
      </div>

      <div class="card px-5 py-4">
        <div class="flex items-center gap-4">
          <div class="flex items-center justify-center w-10 h-10 rounded-lg bg-success-50 text-success-500">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/>
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ stats.onlineDevices }}</div>
            <div class="text-xs text-gray-500">在线设备</div>
          </div>
        </div>
      </div>

      <div class="card px-5 py-4">
        <div class="flex items-center gap-4">
          <div class="flex items-center justify-center w-10 h-10 rounded-lg bg-warning-50 text-warning-500">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ stats.totalPolicies }}</div>
            <div class="text-xs text-gray-500">策略总数</div>
          </div>
        </div>
      </div>

      <div class="card px-5 py-4">
        <div class="flex items-center gap-4">
          <div class="flex items-center justify-center w-10 h-10 rounded-lg bg-primary-50 text-primary-500">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <div>
            <div class="text-2xl font-bold text-gray-900">{{ stats.appliedPolicies }}</div>
            <div class="text-xs text-gray-500">已应用策略</div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card">
        <div class="card-header">
          <h3 class="text-sm font-semibold text-gray-900">快速操作</h3>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-2 gap-3">
            <router-link to="/devices/register" class="flex items-center gap-3 px-4 py-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors group">
              <div class="flex items-center justify-center w-8 h-8 rounded-md bg-gray-100 group-hover:bg-primary-100 text-gray-500 group-hover:text-primary-500 transition-colors">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
              </div>
              <span class="text-sm font-medium text-gray-700 group-hover:text-primary-600">注册设备</span>
            </router-link>
            <router-link to="/policies/generate" class="flex items-center gap-3 px-4 py-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors group">
              <div class="flex items-center justify-center w-8 h-8 rounded-md bg-gray-100 group-hover:bg-primary-100 text-gray-500 group-hover:text-primary-500 transition-colors">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
              </div>
              <span class="text-sm font-medium text-gray-700 group-hover:text-primary-600">生成策略</span>
            </router-link>
            <router-link to="/groups/address" class="flex items-center gap-3 px-4 py-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors group">
              <div class="flex items-center justify-center w-8 h-8 rounded-md bg-gray-100 group-hover:bg-primary-100 text-gray-500 group-hover:text-primary-500 transition-colors">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
              </div>
              <span class="text-sm font-medium text-gray-700 group-hover:text-primary-600">地址组</span>
            </router-link>
            <router-link to="/policies" class="flex items-center gap-3 px-4 py-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors group">
              <div class="flex items-center justify-center w-8 h-8 rounded-md bg-gray-100 group-hover:bg-primary-100 text-gray-500 group-hover:text-primary-500 transition-colors">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>
              </div>
              <span class="text-sm font-medium text-gray-700 group-hover:text-primary-600">策略列表</span>
            </router-link>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="text-sm font-semibold text-gray-900">平台特性</h3>
        </div>
        <div class="card-body">
          <ul class="space-y-2.5">
            <li v-for="f in features" :key="f" class="flex items-start gap-2 text-sm text-gray-600">
              <svg class="w-4 h-4 text-success-500 mt-0.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>
              <span>{{ f }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header flex items-center justify-between">
        <h3 class="text-sm font-semibold text-gray-900">最新策略</h3>
        <router-link to="/policies" class="text-xs text-primary-500 hover:text-primary-600 font-medium">查看全部</router-link>
      </div>
      <div class="card-body">
        <div v-if="loading" class="py-8 text-center text-sm text-gray-400">加载中...</div>
        <div v-else-if="recentPolicies.length === 0" class="empty-state py-12">
          <svg class="w-12 h-12 text-gray-300 mx-auto mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>
          <p class="text-sm text-gray-400 mb-3">暂无策略记录</p>
          <router-link to="/policies/generate" class="btn-primary btn-sm">创建第一个策略</router-link>
        </div>
        <div v-else class="table-container">
          <table class="data-table">
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
                <td class="font-medium text-gray-900">{{ policy.policy_name }}</td>
                <td class="font-mono text-xs">{{ policy.source_ip }}</td>
                <td class="font-mono text-xs">{{ policy.dest_ip }}</td>
                <td><span class="badge-gray">{{ policy.protocol?.toUpperCase() }}</span></td>
                <td class="font-mono text-xs">{{ policy.dest_port }}</td>
                <td><span :class="statusBadge(policy.status)">{{ statusText(policy.status) }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { deviceAPI, policyAPI } from '../services/api'

const stats = ref({ totalDevices: 0, onlineDevices: 0, totalPolicies: 0, appliedPolicies: 0 })
const recentPolicies = ref([])
const loading = ref(false)

const features = [
  '支持华为、山石、新华三、瞻博四大品牌防火墙',
  '统一适配层，自动适配不同厂商 CLI 命令',
  '智能路径计算，自动识别流量经过的防火墙',
  '策略模板库，基于 Jinja2 标准化生成',
  '审核流程，策略下发前人工确认',
  'API 接口，便于集成和自动化',
]

const statusBadge = (s) => ({ applied: 'badge-success', pending: 'badge-warning', failed: 'badge-danger' }[s] || 'badge-gray')
const statusText = (s) => ({ applied: '已应用', pending: '待应用', failed: '失败' }[s] || s)

onMounted(async () => {
  loading.value = true
  try {
    const [dRes, pRes] = await Promise.all([deviceAPI.getAll(), policyAPI.getAll()])
    stats.value.totalDevices = dRes.data.count || 0
    stats.value.onlineDevices = dRes.data.devices?.filter(d => d.status === 'online').length || 0
    stats.value.totalPolicies = pRes.data.count || 0
    stats.value.appliedPolicies = pRes.data.policies?.filter(p => p.status === 'applied').length || 0
    recentPolicies.value = pRes.data.policies?.slice(-5).reverse() || []
  } catch (e) {
    console.error('加载统计数据失败:', e)
  } finally {
    loading.value = false
  }
})
</script>
