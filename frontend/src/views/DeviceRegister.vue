<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">注册新设备</h1>
        <p class="page-desc">添加防火墙设备到平台管理</p>
      </div>
      <router-link to="/devices" class="btn-default">返回列表</router-link>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 card">
        <div class="card-header"><h3 class="text-sm font-semibold text-gray-900">设备信息</h3></div>
        <div class="card-body">
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="form-label">设备名称 *</label>
                <input v-model="form.name" type="text" class="form-input" placeholder="例如：huawei_fw_01" required />
              </div>
              <div>
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
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="form-label">IP地址 *</label>
                <input v-model="form.ip" type="text" class="form-input" placeholder="例如：192.168.1.10" required />
              </div>
              <div>
                <label class="form-label">端口</label>
                <input v-model="form.port" type="number" class="form-input" placeholder="默认：22" />
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="form-label">用户名</label>
                <input v-model="form.username" type="text" class="form-input" placeholder="SSH用户名" />
              </div>
              <div>
                <label class="form-label">密码</label>
                <input v-model="form.password" type="password" class="form-input" placeholder="SSH密码" />
              </div>
            </div>
            <div>
              <label class="form-label">位置</label>
              <input v-model="form.location" type="text" class="form-input" placeholder="例如：数据中心A" />
            </div>
            <div class="flex gap-3 pt-2">
              <button type="submit" class="btn-primary" :disabled="submitting">{{ submitting ? '注册中...' : '注册设备' }}</button>
              <button type="button" class="btn-default" @click="resetForm">重置</button>
            </div>
          </form>

          <div v-if="message" :class="['mt-4 px-4 py-3 rounded-md text-sm', message.type === 'success' ? 'bg-success-50 text-success-700 border border-success-200' : 'bg-danger-50 text-danger-700 border border-danger-200']">
            {{ message.text }}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3 class="text-sm font-semibold text-gray-900">填写说明</h3></div>
        <div class="card-body">
          <ul class="space-y-3 text-sm text-gray-600">
            <li><span class="font-medium text-gray-900">设备名称：</span>全局唯一标识，建议使用有意义的命名</li>
            <li><span class="font-medium text-gray-900">厂商：</span>支持华为、山石、新华三、瞻博</li>
            <li><span class="font-medium text-gray-900">IP地址：</span>防火墙的管理接口IP</li>
            <li><span class="font-medium text-gray-900">端口：</span>SSH管理端口，默认22</li>
            <li><span class="font-medium text-gray-900">用户名/密码：</span>用于SSH连接，建议管理员账户</li>
            <li><span class="font-medium text-gray-900">位置：</span>可选，标识设备所在位置</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { deviceAPI } from '../services/api'

const router = useRouter()
const form = ref({ name: '', vendor: '', ip: '', port: 22, username: '', password: '', location: '' })
const submitting = ref(false)
const message = ref('')

const handleSubmit = async () => {
  submitting.value = true; message.value = ''
  try {
    const r = await deviceAPI.register(form.value)
    if (r.data.status === 'registered' || r.data.status === 'updated') {
      message.value = { type: 'success', text: r.data.message }
      setTimeout(() => router.push('/devices'), 1500)
    }
  } catch (e) { message.value = { type: 'error', text: '注册失败：' + (e.response?.data?.detail || e.message) } }
  finally { submitting.value = false }
}

const resetForm = () => { form.value = { name: '', vendor: '', ip: '', port: 22, username: '', password: '', location: '' }; message.value = '' }
</script>
