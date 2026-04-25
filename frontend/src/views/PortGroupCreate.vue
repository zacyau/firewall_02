<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">创建端口组</h1>
        <p class="page-desc">创建新的端口组</p>
      </div>
      <router-link to="/groups/port" class="btn-default">返回列表</router-link>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 card">
        <div class="card-header"><h3 class="text-sm font-semibold text-gray-900">端口组信息</h3></div>
        <div class="card-body">
          <form @submit.prevent="submitForm" class="space-y-4">
            <div>
              <label class="form-label">组名称 *</label>
              <input v-model="form.name" type="text" class="form-input" placeholder="例如：web_ports" required />
            </div>
            <div>
              <label class="form-label">描述</label>
              <input v-model="form.description" type="text" class="form-input" placeholder="可选的描述信息" />
            </div>
            <div>
              <label class="form-label">协议 *</label>
              <select v-model="form.protocol" class="form-select" required>
                <option value="tcp">TCP</option>
                <option value="udp">UDP</option>
                <option value="icmp">ICMP</option>
              </select>
            </div>
            <div>
              <label class="form-label">端口列表 *</label>
              <textarea v-model="portsText" class="form-input font-mono" rows="6" placeholder="80&#10;443&#10;8080-8090" required></textarea>
              <p class="text-xs text-gray-400 mt-1">每行一个端口或范围(如8080-8090)</p>
            </div>
            <div v-if="parsedPorts.length > 0">
              <label class="form-label">预览 ({{ parsedPorts.length }} 个端口)</label>
              <div class="flex flex-wrap gap-1.5 p-3 bg-gray-50 rounded-lg">
                <span v-for="(port, idx) in parsedPorts" :key="idx" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-warning-50 text-warning-600">
                  {{ port }}
                </span>
              </div>
            </div>
            <div class="flex gap-3 pt-2">
              <button type="submit" class="btn-primary" :disabled="submitting">{{ submitting ? '创建中...' : '创建端口组' }}</button>
              <router-link to="/groups/port" class="btn-default">取消</router-link>
            </div>
          </form>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3 class="text-sm font-semibold text-gray-900">填写说明</h3></div>
        <div class="card-body">
          <ul class="space-y-3 text-sm text-gray-600">
            <li><span class="font-medium text-gray-900">组名称：</span>全局唯一标识，建议使用有意义的英文命名</li>
            <li><span class="font-medium text-gray-900">协议：</span>选择端口组使用的协议类型</li>
            <li><span class="font-medium text-gray-900">端口格式：</span>支持单端口(80)和范围(8080-8090)</li>
            <li><span class="font-medium text-gray-900">每行一个：</span>端口列表中每行填写一个端口条目</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { portGroupAPI } from '../services/api'

const router = useRouter()
const form = ref({ name: '', description: '', protocol: 'tcp' })
const portsText = ref('')
const submitting = ref(false)

const parsedPorts = computed(() => {
  if (!portsText.value) return []
  return portsText.value.split('\n').map(p => p.trim()).filter(p => p)
})

const submitForm = async () => {
  if (!parsedPorts.value.length) { alert('请至少添加一个端口'); return }
  submitting.value = true
  try {
    await portGroupAPI.create({ name: form.value.name, description: form.value.description, protocol: form.value.protocol, ports: parsedPorts.value })
    alert('端口组创建成功！'); router.push('/groups/port')
  } catch (e) { alert('创建失败：' + (e.response?.data?.detail || e.message)) }
  finally { submitting.value = false }
}
</script>
