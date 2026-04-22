<template>
  <div class="device-register">
    <div class="page-header">
      <div>
        <h1 class="page-title">➕ 注册新设备</h1>
        <p class="page-description">添加防火墙设备到平台管理</p>
      </div>
    </div>

    <div class="card">
      <form @submit.prevent="handleSubmit">
        <div class="grid grid-2">
          <div class="form-group">
            <label class="form-label">设备名称 *</label>
            <input 
              v-model="form.name"
              type="text" 
              class="form-input" 
              placeholder="例如：huawei_fw_01"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">厂商 *</label>
            <select v-model="form.vendor" class="form-select" required>
              <option value="">请选择厂商</option>
              <option value="huawei">华为</option>
              <option value="hillstone">山石</option>
              <option value="h3c">新华三</option>
              <option value="juniper">瞻博</option>
            </select>
          </div>
        </div>

        <div class="grid grid-2">
          <div class="form-group">
            <label class="form-label">IP地址 *</label>
            <input 
              v-model="form.ip"
              type="text" 
              class="form-input" 
              placeholder="例如：192.168.1.10"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">端口</label>
            <input 
              v-model="form.port"
              type="number" 
              class="form-input" 
              placeholder="默认：22"
            />
          </div>
        </div>

        <div class="grid grid-2">
          <div class="form-group">
            <label class="form-label">用户名</label>
            <input 
              v-model="form.username"
              type="text" 
              class="form-input" 
              placeholder="SSH用户名"
            />
          </div>

          <div class="form-group">
            <label class="form-label">密码</label>
            <input 
              v-model="form.password"
              type="password" 
              class="form-input" 
              placeholder="SSH密码"
            />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">位置</label>
          <input 
            v-model="form.location"
            type="text" 
            class="form-input" 
            placeholder="例如：数据中心A"
          />
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="submitting">
            {{ submitting ? '注册中...' : '✅ 注册设备' }}
          </button>
          <button type="button" class="btn" @click="resetForm" style="background: #999; color: white;">
            🔄 重置
          </button>
        </div>
      </form>

      <div v-if="message" :class="['message', message.type]">
        {{ message.text }}
      </div>
    </div>

    <div class="card mt-4">
      <h3 class="card-title">💡 填写说明</h3>
      <ul class="info-list">
        <li><strong>设备名称：</strong>全局唯一标识，建议使用有意义的命名，如 huawei_fw_01</li>
        <li><strong>厂商：</strong>支持的厂商有华为、山石、新华三、瞻博</li>
        <li><strong>IP地址：</strong>防火墙的管理接口IP</li>
        <li><strong>端口：</strong>SSH管理端口，默认为22</li>
        <li><strong>用户名/密码：</strong>用于SSH连接和CLI操作，建议使用管理员账户</li>
        <li><strong>位置：</strong>可选，用于标识设备所在位置</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { deviceAPI } from '../services/api'

const router = useRouter()
const form = ref({
  name: '',
  vendor: '',
  ip: '',
  port: 22,
  username: '',
  password: '',
  location: ''
})

const submitting = ref(false)
const message = ref('')

const handleSubmit = async () => {
  submitting.value = true
  message.value = ''

  try {
    const response = await deviceAPI.register(form.value)
    
    if (response.data.status === 'registered') {
      message.value = {
        type: 'success',
        text: `✅ ${response.data.message}`
      }
      setTimeout(() => {
        router.push('/devices')
      }, 1500)
    } else if (response.data.status === 'updated') {
      message.value = {
        type: 'success',
        text: `✅ ${response.data.message}`
      }
    }
  } catch (error) {
    message.value = {
      type: 'error',
      text: '❌ 注册失败：' + (error.response?.data?.detail || error.message)
    }
    console.error('注册设备失败:', error)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  form.value = {
    name: '',
    vendor: '',
    ip: '',
    port: 22,
    username: '',
    password: '',
    location: ''
  }
  message.value = ''
}
</script>

<style scoped>
.form-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}

.message {
  margin-top: 16px;
  padding: 12px;
  border-radius: 6px;
}

.message.success {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}

.message.error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
}

.info-list {
  list-style: none;
  padding: 0;
}

.info-list li {
  padding: 8px 0;
  font-size: 14px;
  color: #666;
  border-bottom: 1px solid #f0f0f0;
}

.info-list li:last-child {
  border-bottom: none;
}

.info-list strong {
  color: #333;
}
</style>
