<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">创建地址组</h1>
        <p class="page-desc">创建新的IP地址组</p>
      </div>
      <router-link to="/groups/address" class="btn-default">返回列表</router-link>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 card">
        <div class="card-header"><h3 class="text-sm font-semibold text-gray-900">地址组信息</h3></div>
        <div class="card-body">
          <form @submit.prevent="submitForm" class="space-y-4">
            <div>
              <label class="form-label">组名称 *</label>
              <input v-model="form.name" type="text" class="form-input" placeholder="例如：web_servers" required />
            </div>
            <div>
              <label class="form-label">描述</label>
              <input v-model="form.description" type="text" class="form-input" placeholder="可选的描述信息" />
            </div>
            <div>
              <label class="form-label">地址列表 *</label>
              <textarea v-model="addressesText" class="form-input font-mono" rows="6" placeholder="192.168.1.1&#10;192.168.1.2&#10;10.0.0.0/24" required></textarea>
              <p class="text-xs text-gray-400 mt-1">每行一个IP地址或网段(CIDR格式)</p>
            </div>
            <div v-if="parsedAddresses.length > 0">
              <label class="form-label">预览 ({{ parsedAddresses.length }} 个地址)</label>
              <div class="flex flex-wrap gap-1.5 p-3 bg-gray-50 rounded-lg">
                <span v-for="(addr, idx) in parsedAddresses" :key="idx" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono bg-primary-50 text-primary-600">
                  {{ addr }}
                </span>
              </div>
            </div>
            <div class="flex gap-3 pt-2">
              <button type="submit" class="btn-primary" :disabled="submitting">{{ submitting ? '创建中...' : '创建地址组' }}</button>
              <router-link to="/groups/address" class="btn-default">取消</router-link>
            </div>
          </form>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3 class="text-sm font-semibold text-gray-900">填写说明</h3></div>
        <div class="card-body">
          <ul class="space-y-3 text-sm text-gray-600">
            <li><span class="font-medium text-gray-900">组名称：</span>全局唯一标识，建议使用有意义的英文命名</li>
            <li><span class="font-medium text-gray-900">地址格式：</span>支持单IP(192.168.1.1)和CIDR网段(10.0.0.0/24)</li>
            <li><span class="font-medium text-gray-900">每行一个：</span>地址列表中每行填写一个地址条目</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { addressGroupAPI } from '../services/api'

const router = useRouter()
const form = ref({ name: '', description: '' })
const addressesText = ref('')
const submitting = ref(false)

const parsedAddresses = computed(() => {
  if (!addressesText.value) return []
  return addressesText.value.split('\n').map(a => a.trim()).filter(a => a)
})

const submitForm = async () => {
  if (!parsedAddresses.value.length) { alert('请至少添加一个地址'); return }
  submitting.value = true
  try {
    await addressGroupAPI.create({ name: form.value.name, description: form.value.description, addresses: parsedAddresses.value })
    alert('地址组创建成功！'); router.push('/groups/address')
  } catch (e) { alert('创建失败：' + (e.response?.data?.detail || e.message)) }
  finally { submitting.value = false }
}
</script>
