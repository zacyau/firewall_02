<template>
  <div class="address-group-list">
    <div class="page-header">
      <div class="flex flex-between">
        <div>
          <h1 class="page-title">📍 地址组管理</h1>
          <p class="page-description">管理IP地址组，用于策略配置</p>
        </div>
        <router-link to="/groups/address/create" class="btn btn-primary">
          + 创建地址组
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>

    <div v-else-if="groups.length === 0" class="card empty-state">
      <div class="empty-state-icon">📍</div>
      <p>暂无地址组</p>
      <router-link to="/groups/address/create" class="btn btn-primary">
        创建第一个地址组
      </router-link>
    </div>

    <div v-else class="groups-grid">
      <div v-for="group in groups" :key="group.id" class="group-card">
        <div class="group-card-header">
          <div>
            <div class="group-card-name">{{ group.name }}</div>
            <div class="group-card-desc">{{ group.description || '无描述' }}</div>
          </div>
          <div class="group-card-actions">
            <button class="btn btn-sm" @click="editGroup(group)">编辑</button>
            <button class="btn btn-sm btn-danger" @click="confirmDelete(group)">删除</button>
          </div>
        </div>
        <div class="group-card-content">
          <div class="meta-label">地址数量: <span class="badge badge-info">{{ group.addresses?.length || 0 }}</span></div>
          <div class="addresses-preview">
            <span v-for="(addr, idx) in (group.addresses || [])" :key="idx" class="addr-tag">
              {{ addr }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal-content">
        <h3>编辑地址组</h3>
        <form @submit.prevent="submitEdit">
          <div class="form-group">
            <label class="form-label">组名称</label>
            <input v-model="editForm.name" type="text" class="form-input" disabled />
          </div>
          <div class="form-group">
            <label class="form-label">描述</label>
            <input v-model="editForm.description" type="text" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">地址列表</label>
            <textarea
              v-model="addressesText"
              class="form-input"
              rows="6"
              style="font-family: monospace;"
              placeholder="192.168.1.1
192.168.1.2
10.0.0.0/24"
            ></textarea>
            <small>每行一个IP地址或网段(CIDR格式)</small>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? '保存中...' : '保存修改' }}
            </button>
            <button type="button" class="btn" @click="showEditModal = false" style="background: #999; color: white;">
              取消
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { addressGroupAPI } from '../services/api'

const groups = ref([])
const loading = ref(false)
const error = ref('')
const showEditModal = ref(false)
const editForm = ref({ id: null, name: '', description: '', addresses: [] })
const addressesText = ref('')
const submitting = ref(false)

const loadGroups = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await addressGroupAPI.getAll()
    groups.value = response.data.groups || []
  } catch (err) {
    error.value = '加载地址组失败：' + (err.message || '未知错误')
  } finally {
    loading.value = false
  }
}

const editGroup = (group) => {
  editForm.value = { ...group }
  addressesText.value = (group.addresses || []).join('\n')
  showEditModal.value = true
}

const submitEdit = async () => {
  submitting.value = true
  try {
    const addresses = addressesText.value.split('\n').map(a => a.trim()).filter(a => a)
    await addressGroupAPI.update(editForm.value.name, {
      name: editForm.value.name,
      description: editForm.value.description,
      addresses: addresses
    })
    alert('✅ 地址组更新成功！')
    showEditModal.value = false
    await loadGroups()
  } catch (err) {
    alert('❌ 更新失败：' + (err.response?.data?.detail || err.message))
  } finally {
    submitting.value = false
  }
}

const confirmDelete = async (group) => {
  if (!confirm(`确定要删除地址组 "${group.name}" 吗？`)) return

  try {
    await addressGroupAPI.delete(group.name)
    alert('✅ 地址组删除成功！')
    await loadGroups()
  } catch (err) {
    alert('❌ 删除失败：' + (err.response?.data?.detail || err.message))
  }
}

onMounted(() => {
  loadGroups()
})
</script>

<style scoped>
.addresses-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.addr-tag {
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-family: monospace;
}

.more-count {
  color: #999;
  font-size: 12px;
}

.addresses-cell {
  max-width: 300px;
}
</style>
