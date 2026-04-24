<template>
  <div class="address-group-create">
    <div class="page-header">
      <div class="flex flex-between">
        <div>
          <h1 class="page-title">📍 创建地址组</h1>
          <p class="page-description">创建新的IP地址组</p>
        </div>
        <router-link to="/groups/address" class="btn">
          返回列表
        </router-link>
      </div>
    </div>

    <div class="card">
      <form @submit.prevent="submitForm">
        <div class="form-group">
          <label class="form-label">组名称 *</label>
          <input
            v-model="form.name"
            type="text"
            class="form-input"
            placeholder="例如：web_servers"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label">描述</label>
          <input
            v-model="form.description"
            type="text"
            class="form-input"
            placeholder="可选的描述信息"
          />
        </div>

        <div class="form-group">
          <label class="form-label">地址列表 *</label>
          <textarea
            v-model="addressesText"
            class="form-input"
            rows="6"
            style="font-family: monospace;"
            placeholder="192.168.1.1
192.168.1.2
10.0.0.0/24"
            required
          ></textarea>
          <small>每行一个IP地址或网段(CIDR格式)</small>
        </div>

        <div v-if="parsedAddresses.length > 0" class="form-group">
          <label class="form-label">预览 ({{ parsedAddresses.length }} 个地址)</label>
          <div class="addresses-preview">
            <span v-for="(addr, idx) in parsedAddresses" :key="idx" class="addr-tag">
              {{ addr }}
            </span>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="submitting">
            {{ submitting ? '创建中...' : '创建地址组' }}
          </button>
          <router-link to="/groups/address" class="btn" style="background: #999; color: white;">
            取消
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { addressGroupAPI } from '../services/api'

const router = useRouter()
const form = ref({
  name: '',
  description: ''
})
const addressesText = ref('')
const submitting = ref(false)

const parsedAddresses = computed(() => {
  if (!addressesText.value) return []
  return addressesText.value.split('\n').map(a => a.trim()).filter(a => a)
})

const submitForm = async () => {
  if (!parsedAddresses.value.length) {
    alert('请至少添加一个地址')
    return
  }

  submitting.value = true
  try {
    await addressGroupAPI.create({
      name: form.value.name,
      description: form.value.description,
      addresses: parsedAddresses.value
    })
    alert('✅ 地址组创建成功！')
    router.push('/groups/address')
  } catch (err) {
    alert('❌ 创建失败：' + (err.response?.data?.detail || err.message))
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.addresses-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.addr-tag {
  background: #e6f7ff;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-family: monospace;
  color: #1890ff;
  border: 1px solid #91d5ff;
}
</style>
