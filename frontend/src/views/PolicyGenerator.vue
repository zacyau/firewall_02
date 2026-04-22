<template>
  <div class="policy-generator">
    <div class="page-header">
      <h1 class="page-title">⚡ 策略生成</h1>
      <p class="page-description">基于防火墙路径计算，自动生成策略脚本</p>
    </div>

    <div class="grid grid-2">
      <!-- 策略配置表单 -->
      <div class="card">
        <h3 class="card-title">📝 策略配置</h3>
        <form @submit.prevent="generatePolicy">
          <div class="form-group">
            <label class="form-label">策略名称 *</label>
            <input 
              v-model="form.policy_name"
              type="text" 
              class="form-input" 
              placeholder="例如：web_https_access"
              required
            />
          </div>

          <div class="grid grid-2">
            <div class="form-group">
              <label class="form-label">源IP地址 *</label>
              <input 
                v-model="form.source_ip"
                type="text" 
                class="form-input" 
                placeholder="例如：10.0.1.100"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label">目标IP地址 *</label>
              <input 
                v-model="form.dest_ip"
                type="text" 
                class="form-input" 
                placeholder="例如：10.0.2.200"
                required
              />
            </div>
          </div>

          <div class="grid grid-2">
            <div class="form-group">
              <label class="form-label">协议 *</label>
              <select v-model="form.protocol" class="form-select" required>
                <option value="tcp">TCP</option>
                <option value="udp">UDP</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">目标端口 *</label>
              <input 
                v-model="form.dest_port"
                type="text" 
                class="form-input" 
                placeholder="例如：443 或 8000-9000"
                required
              />
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="generating">
              {{ generating ? '生成中...' : '⚡ 生成策略' }}
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

      <!-- 防火墙路径预览 -->
      <div class="card">
        <h3 class="card-title">🛤️ 防火墙路径及Zone配置</h3>
        <div v-if="!generatedData.firewall_policies?.length" class="empty-state">
          <p>配置左侧表单后点击"生成策略"查看防火墙路径</p>
        </div>
        <div v-else class="path-preview">
          <div class="path-summary mb-4">
            <strong>路径摘要：</strong>{{ generatedData.path_summary }}
          </div>
          <div 
            v-for="(fw, index) in generatedData.firewall_policies" 
            :key="index"
            class="path-item"
          >
            <div class="path-step">
              <div class="step-number">
                {{ index + 1 }}
                <div class="step-direction">{{ fw.flow_direction }}</div>
              </div>
              <div class="step-content">
                <div class="device-info">
                  <span class="vendor-icon">{{ getVendorIcon(fw.device_name) }}</span>
                  <strong>{{ fw.device_name }}</strong>
                  <span class="badge" :class="getVendorBadge(fw.vendor)">{{ fw.vendor.toUpperCase() }}</span>
                </div>
                <div class="zone-details">
                  <div class="zone-item">
                    <span class="zone-label">源Zone:</span>
                    <span class="zone-name">{{ fw.source_zone }}</span>
                    <span class="zone-desc">({{ fw.source_zone_description }})</span>
                  </div>
                  <div class="zone-arrow">↓</div>
                  <div class="zone-item">
                    <span class="zone-label">目的Zone:</span>
                    <span class="zone-name">{{ fw.dest_zone }}</span>
                    <span class="zone-desc">({{ fw.dest_zone_description }})</span>
                  </div>
                </div>
                <div class="ip-info">
                  <span>源IP: {{ form.source_ip }}</span>
                  <span>→</span>
                  <span>目的IP: {{ form.dest_ip }}</span>
                </div>
              </div>
            </div>
            <div v-if="index < generatedData.firewall_policies.length - 1" class="path-arrow">
              ↓ 流量经过
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 生成的策略脚本 -->
    <div v-if="generatedData.firewall_policies?.length" class="card mt-4">
      <div class="flex flex-between mb-4">
        <h3 class="card-title">📄 生成的策略脚本</h3>
        <div>
          <button class="btn btn-primary" @click="copyAllScripts">
            📋 复制所有脚本
          </button>
        </div>
      </div>

      <div 
        v-for="(fw, index) in generatedData.firewall_policies" 
        :key="index"
        class="policy-script-item"
      >
        <div class="script-header">
          <h4>
            <span class="vendor-icon">{{ getVendorIcon(fw.device_name) }}</span>
            {{ fw.device_name }}
          </h4>
          <div class="script-actions">
            <button class="btn btn-primary" @click="copyScript(fw.policy_script, fw.device_name)">
              📋 复制
            </button>
            <button 
              class="btn btn-success" 
              @click="applyPolicy(fw)"
              :disabled="applying === fw.device_name"
            >
              {{ applying === fw.device_name ? '应用中...' : '🚀 应用到防火墙' }}
            </button>
          </div>
        </div>
        <div class="script-body">
          <pre class="code-block">{{ fw.policy_script }}</pre>
        </div>
      </div>
    </div>

    <!-- 申请结果弹窗 -->
    <div v-if="showApplyModal" class="modal-overlay" @click="showApplyModal = false">
      <div class="modal-content" @click.stop>
        <h3>🚀 应用结果</h3>
        <div class="modal-body">
          <div v-if="applyResult.loading" class="loading">应用策略中...</div>
          <div v-else-if="applyResult.error" class="error-message">
            {{ applyResult.error }}
          </div>
          <div v-else>
            <div class="result-item">
              <strong>状态：</strong>
              <span :class="['badge', applyResult.status === 'success' ? 'badge-success' : 'badge-error']">
                {{ applyResult.status }}
              </span>
            </div>
            <div class="result-item">
              <strong>设备：</strong>
              <span>{{ applyResult.device_name }}</span>
            </div>
            <div class="result-item">
              <strong>消息：</strong>
              <span>{{ applyResult.message }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-primary" @click="showApplyModal = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { policyAPI } from '../services/api'

const form = ref({
  policy_name: '',
  source_ip: '',
  dest_ip: '',
  protocol: 'tcp',
  dest_port: ''
})

const generating = ref(false)
const applying = ref('')
const generatedData = ref({})
const message = ref('')
const showApplyModal = ref(false)
const applyResult = ref({})

const generatePolicy = async () => {
  generating.value = true
  message.value = ''

  try {
    const response = await policyAPI.generate(form.value)
    generatedData.value = response.data.data || {}
    message.value = {
      type: 'success',
      text: `✅ 策略生成成功！共 ${generatedData.value.firewall_count} 台防火墙需要配置`
    }
  } catch (error) {
    message.value = {
      type: 'error',
      text: '❌ 生成失败：' + (error.response?.data?.detail || error.message)
    }
    console.error('生成策略失败:', error)
  } finally {
    generating.value = false
  }
}

const applyPolicy = async (fwPolicy) => {
  applying.value = fwPolicy.device_name
  applyResult.value = { loading: true }
  showApplyModal.value = true

  try {
    const response = await policyAPI.apply({
      device_name: fwPolicy.device_name,
      policy_script: fwPolicy.policy_script
    })
    applyResult.value = response.data
  } catch (error) {
    applyResult.value = {
      error: '应用失败：' + (error.response?.data?.detail || error.message)
    }
    console.error('应用策略失败:', error)
  } finally {
    applying.value = ''
  }
}

const copyScript = (script, deviceName) => {
  navigator.clipboard.writeText(script)
    .then(() => {
      alert(`✅ ${deviceName} 的策略脚本已复制到剪贴板`)
    })
    .catch(err => {
      console.error('复制失败:', err)
      alert('复制失败，请手动复制')
    })
}

const copyAllScripts = () => {
  const allScripts = generatedData.value.firewall_policies
    .map(fw => `=== ${fw.device_name} ===\n${fw.policy_script}`)
    .join('\n\n')
  
  navigator.clipboard.writeText(allScripts)
    .then(() => {
      alert('✅ 所有策略脚本已复制到剪贴板')
    })
    .catch(err => {
      console.error('复制失败:', err)
    })
}

const getVendorIcon = (deviceName) => {
  if (deviceName.includes('huawei')) return '🔵'
  if (deviceName.includes('hillstone')) return '🟠'
  if (deviceName.includes('h3c')) return '🟢'
  if (deviceName.includes('juniper')) return '🔴'
  return '🖥️'
}

const getVendorBadge = (vendor) => {
  const badges = {
    'huawei': 'vendor-huawei',
    'hillstone': 'vendor-hillstone',
    'h3c': 'vendor-h3c',
    'juniper': 'vendor-juniper'
  }
  return badges[vendor] || ''
}

const resetForm = () => {
  form.value = {
    policy_name: '',
    source_ip: '',
    dest_ip: '',
    protocol: 'tcp',
    dest_port: ''
  }
  generatedData.value = {}
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

.path-preview {
  padding: 16px;
}

.path-summary {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  color: #1890ff;
}

.path-item {
  margin-bottom: 16px;
}

.path-step {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.step-number {
  width: 48px;
  height: 48px;
  background: #1890ff;
  color: white;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 18px;
  flex-shrink: 0;
}

.step-direction {
  font-size: 10px;
  font-weight: normal;
  margin-top: 2px;
}

.step-content {
  flex: 1;
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.device-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e8e8e8;
}

.device-info strong {
  font-size: 18px;
  color: #333;
}

.zone-details {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.zone-item {
  flex: 1;
  background: white;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
}

.zone-label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.zone-name {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 2px;
}

.zone-desc {
  font-size: 12px;
  color: #666;
}

.zone-arrow {
  font-size: 24px;
  color: #1890ff;
  font-weight: bold;
}

.ip-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
  background: white;
  padding: 8px 12px;
  border-radius: 4px;
}

.path-arrow {
  text-align: center;
  font-size: 16px;
  color: #52c41a;
  margin: 12px 0;
  padding: 8px;
  background: #f6ffed;
  border-radius: 4px;
  font-weight: 500;
}

.vendor-huawei {
  background: #e6f7ff;
  color: #1890ff;
}

.vendor-hillstone {
  background: #fff7e6;
  color: #fa8c16;
}

.vendor-h3c {
  background: #f6ffed;
  color: #52c41a;
}

.vendor-juniper {
  background: #fff0f0;
  color: #f5222d;
}

.policy-script-item {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
}

.script-header {
  background: #f5f7fa;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.script-header h4 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.vendor-icon {
  font-size: 24px;
}

.script-actions {
  display: flex;
  gap: 8px;
}

.script-body {
  padding: 16px;
  background: white;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.modal-content h3 {
  margin-bottom: 16px;
  color: #333;
}

.modal-body {
  margin: 20px 0;
}

.result-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

.result-item:last-child {
  border-bottom: none;
}

.modal-footer {
  text-align: right;
  margin-top: 20px;
}
</style>
