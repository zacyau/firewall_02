<template>
  <div class="port-group-create">
    <div class="page-header">
      <div class="flex flex-between">
        <div>
          <h1 class="page-title">🔌 创建端口组</h1>
          <p class="page-description">创建新的端口组</p>
        </div>
        <router-link to="/groups/port" class="btn">
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
            placeholder="例如：web_ports"
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
          <label class="form-label">协议 *</label>
          <select v-model="form.protocol" class="form-input" required>
            <option value="tcp">TCP</option>
            <option value="udp">UDP</option>
            <option value="icmp">ICMP</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">端口列表 *</label>
          <textarea
            v-model="portsText"
            class="form-input"
            rows="6"
            style="font-family: monospace;"
            placeholder="80
443
8080-8090"
            required
          ></textarea>
          <small>每行一个端口或范围(如8080-8090)</small>
        </div>

        <div v-if="parsedPorts.length > 0" class="form-group">
          <label class="form-label">预览 ({{ parsedPorts.length }} 个端口)</label>
          <div class="ports-preview">
            <span v-for="(port, idx) in parsedPorts" :key="idx" class="port-tag">
              {{ port }}
            </span>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="submitting">
            {{ submitting ? '创建中...' : '创建端口组' }}
          </button>
          <router-link to="/groups/port" class="btn" style="background: #999; color: white;">
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
import { portGroupAPI } from '../services/api'

const router = useRouter()
const form = ref({
  name: '',
  description: '',
  protocol: 'tcp'
})
const portsText = ref('')
const submitting = ref(false)

const parsedPorts = computed(() => {
  if (!portsText.value) return []
  return portsText.value.split('\n').map(p => p.trim()).filter(p => p)
})

const submitForm = async () => {
  if (!parsedPorts.value.length) {
    alert('请至少添加一个端口')
    return
  }

  submitting.value = true
  try {
    await portGroupAPI.create({
      name: form.value.name,
      description: form.value.description,
      protocol: form.value.protocol,
      ports: parsedPorts.value
    })
    alert('✅ 端口组创建成功！')
    router.push('/groups/port')
  } catch (err) {
    alert('❌ 创建失败：' + (err.response?.data?.detail || err.message))
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.ports-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.port-tag {
  background: #fff7e6;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-family: monospace;
  color: #fa8c16;
  border: 1px solid #ffd591;
}
</style>
