<template>
  <div class="port-group-list">
    <div class="page-header">
      <div class="flex flex-between">
        <div>
          <h1 class="page-title">🔌 端口组管理</h1>
          <p class="page-description">管理端口组，用于策略配置</p>
        </div>
        <router-link to="/groups/port/create" class="btn btn-primary">
          + 创建端口组
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>

    <div v-else-if="groups.length === 0" class="card empty-state">
      <div class="empty-state-icon">🔌</div>
      <p>暂无端口组</p>
      <router-link to="/groups/port/create" class="btn btn-primary">
        创建第一个端口组
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
          <div class="meta-label">
            协议: <span class="badge">{{ group.protocol?.toUpperCase() || 'TCP' }}</span>
            &nbsp;&nbsp;
            端口数量: <span class="badge badge-info">{{ group.ports?.length || 0 }}</span>
          </div>
          <div class="ports-preview">
            <span v-for="(port, idx) in (group.ports || [])" :key="idx" class="port-tag">
              {{ port }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal-content">
        <h3>编辑端口组</h3>
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
            <label class="form-label">协议</label>
            <select v-model="editForm.protocol" class="form-input">
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
              <option value="icmp">ICMP</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">端口列表</label>
            <textarea
              v-model="portsText"
              class="form-input"
              rows="6"
              style="font-family: monospace;"
              placeholder="80
443
8080-8090"
            ></textarea>
            <small>每行一个端口或范围(如8080-8090)</small>
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
import { portGroupAPI } from '../services/api'

const groups = ref([])
const loading = ref(false)
const error = ref('')
const showEditModal = ref(false)
const editForm = ref({ id: null, name: '', description: '', protocol: 'tcp', ports: [] })
const portsText = ref('')
const submitting = ref(false)

const loadGroups = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await portGroupAPI.getAll()
    groups.value = response.data.groups || []
  } catch (err) {
    error.value = '加载端口组失败：' + (err.message || '未知错误')
  } finally {
    loading.value = false
  }
}

const editGroup = (group) => {
  editForm.value = { ...group }
  portsText.value = (group.ports || []).join('\n')
  showEditModal.value = true
}

const submitEdit = async () => {
  submitting.value = true
  try {
    const ports = portsText.value.split('\n').map(p => p.trim()).filter(p => p)
    await portGroupAPI.update(editForm.value.name, {
      name: editForm.value.name,
      description: editForm.value.description,
      protocol: editForm.value.protocol,
      ports: ports
    })
    alert('✅ 端口组更新成功！')
    showEditModal.value = false
    await loadGroups()
  } catch (err) {
    alert('❌ 更新失败：' + (err.response?.data?.detail || err.message))
  } finally {
    submitting.value = false
  }
}

const confirmDelete = async (group) => {
  if (!confirm(`确定要删除端口组 "${group.name}" 吗？`)) return

  try {
    await portGroupAPI.delete(group.name)
    alert('✅ 端口组删除成功！')
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
.ports-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.port-tag {
  background: #e6f7ff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-family: monospace;
  color: #1890ff;
}

.more-count {
  color: #999;
  font-size: 12px;
}

.ports-cell {
  max-width: 200px;
}
</style>
