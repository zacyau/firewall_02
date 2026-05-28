<template>
  <div class="space-y-4">
    <div class="card p-4">
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2">
          <label class="text-sm text-gray-600">级别</label>
          <select v-model="filters.level" class="input-field w-28" @change="loadLogs">
            <option value="">全部</option>
            <option value="DEBUG">DEBUG</option>
            <option value="INFO">INFO</option>
            <option value="WARNING">WARNING</option>
            <option value="ERROR">ERROR</option>
          </select>
        </div>
        <div class="flex items-center gap-2">
          <label class="text-sm text-gray-600">关键词</label>
          <input v-model="filters.keyword" class="input-field w-48" placeholder="搜索关键词" @keyup.enter="loadLogs" />
        </div>
        <div class="flex items-center gap-2">
          <label class="text-sm text-gray-600">行数</label>
          <select v-model="filters.lines" class="input-field w-24" @change="loadLogs">
            <option :value="100">100</option>
            <option :value="200">200</option>
            <option :value="500">500</option>
            <option :value="1000">1000</option>
          </select>
        </div>
        <div class="flex items-center gap-2 ml-auto">
          <button class="btn-primary text-sm" @click="loadLogs">
            <svg class="w-4 h-4 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 4v6h6M23 20v-6h-6"/><path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15"/>
            </svg>
            刷新
          </button>
          <button class="btn-secondary text-sm" @click="confirmClear">
            <svg class="w-4 h-4 mr-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
            </svg>
            清空
          </button>
        </div>
      </div>
    </div>

    <div class="card p-4">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-4 text-sm text-gray-500">
          <span>共 {{ logLines.length }} 条</span>
          <span v-if="logInfo.file_size_mb !== undefined">文件大小: {{ logInfo.file_size_mb }} MB</span>
          <span v-if="logInfo.backup_count !== undefined">备份文件: {{ logInfo.backup_count }} 个</span>
        </div>
        <div class="flex items-center gap-2">
          <label class="flex items-center gap-1.5 text-sm text-gray-600 cursor-pointer">
            <input type="checkbox" v-model="autoRefresh" class="rounded border-gray-300" />
            自动刷新
          </label>
          <select v-model="autoRefreshInterval" class="input-field w-20 text-sm" :disabled="!autoRefresh">
            <option :value="5">5s</option>
            <option :value="10">10s</option>
            <option :value="30">30s</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-12 text-gray-400">
        <svg class="animate-spin w-6 h-6 mr-2" viewBox="0 0 24 24" fill="none">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        加载中...
      </div>

      <div v-else-if="logLines.length === 0" class="text-center py-12 text-gray-400 text-sm">
        暂无日志记录
      </div>

      <div v-else class="bg-gray-900 rounded-lg overflow-hidden">
        <div class="overflow-x-auto max-h-[600px] overflow-y-auto font-mono text-xs leading-5">
          <table class="w-full">
            <tbody>
              <tr v-for="(line, idx) in logLines" :key="idx" :class="getLogLevelClass(line)">
                <td class="px-3 py-0.5 text-gray-500 text-right w-12 select-none border-r border-gray-700">{{ idx + 1 }}</td>
                <td class="px-3 py-0.5 whitespace-pre-wrap break-all">{{ line }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="showClearConfirm" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showClearConfirm = false">
      <div class="bg-white rounded-lg shadow-xl p-6 w-96">
        <h3 class="text-lg font-medium text-gray-900 mb-2">确认清空日志</h3>
        <p class="text-sm text-gray-500 mb-4">此操作将清空所有日志记录，不可恢复。确定要继续吗？</p>
        <div class="flex justify-end gap-2">
          <button class="btn-secondary text-sm" @click="showClearConfirm = false">取消</button>
          <button class="btn-danger text-sm" @click="clearLogs">确认清空</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { logAPI } from '../services/api'

const logLines = ref([])
const logInfo = ref({})
const loading = ref(false)
const autoRefresh = ref(false)
const autoRefreshInterval = ref(10)
const showClearConfirm = ref(false)
let timer = null

const filters = ref({
  level: '',
  keyword: '',
  lines: 200
})

async function loadLogs() {
  loading.value = true
  try {
    const params = { lines: filters.value.lines }
    if (filters.value.level) params.level = filters.value.level
    if (filters.value.keyword) params.keyword = filters.value.keyword

    const res = await logAPI.getLogs(params)
    logLines.value = res.data.lines || []
  } catch (e) {
    console.error('加载日志失败:', e)
  } finally {
    loading.value = false
  }
}

async function loadLogInfo() {
  try {
    const res = await logAPI.getInfo()
    logInfo.value = res.data
  } catch (e) {
    console.error('加载日志信息失败:', e)
  }
}

async function clearLogs() {
  showClearConfirm.value = false
  try {
    await logAPI.clearLogs()
    logLines.value = []
    await loadLogInfo()
  } catch (e) {
    console.error('清空日志失败:', e)
  }
}

function confirmClear() {
  showClearConfirm.value = true
}

function getLogLevelClass(line) {
  if (line.includes(' ERROR ')) return 'bg-red-900/30 text-red-300'
  if (line.includes(' WARNING ')) return 'bg-yellow-900/20 text-yellow-300'
  if (line.includes(' DEBUG ')) return 'text-gray-400'
  return 'text-gray-200'
}

function startAutoRefresh() {
  stopAutoRefresh()
  if (autoRefresh.value) {
    timer = setInterval(() => {
      loadLogs()
      loadLogInfo()
    }, autoRefreshInterval.value * 1000)
  }
}

function stopAutoRefresh() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

watch(autoRefresh, (val) => {
  if (val) startAutoRefresh()
  else stopAutoRefresh()
})

watch(autoRefreshInterval, () => {
  if (autoRefresh.value) startAutoRefresh()
})

onMounted(() => {
  loadLogs()
  loadLogInfo()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>
