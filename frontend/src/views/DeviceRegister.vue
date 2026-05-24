<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="page-title">{{ isEdit ? '编辑设备' : '添加设备' }}</h1>
        <p class="page-desc">通过配置文件管理防火墙设备</p>
      </div>
      <router-link to="/devices" class="btn-default">返回列表</router-link>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 card">
        <div class="card-header">
          <h3 class="text-sm font-semibold text-gray-900">{{ isEdit ? '编辑设备配置' : '新建设备配置' }}</h3>
        </div>
        <div class="card-body">
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="form-label">设备名称 *</label>
                <input v-model="form.name" type="text" class="form-input" placeholder="例如：FW_01" :disabled="isEdit" required />
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
                <input v-model.number="form.port" type="number" class="form-input" placeholder="默认：22" />
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
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="form-label">位置</label>
                <input v-model="form.location" type="text" class="form-input" placeholder="例如：数据中心A" />
              </div>
              <div>
                <label class="form-label">描述</label>
                <input v-model="form.description" type="text" class="form-input" placeholder="设备描述" />
              </div>
            </div>

            <div class="border-t pt-4 mt-4">
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-sm font-medium text-gray-900">安全区域配置</h4>
                <div class="flex gap-2">
                  <select v-model="newZoneType" class="form-select text-sm py-1">
                    <option value="">选择区域类型</option>
                    <option value="edge">edge - 末端区域</option>
                    <option value="forward-in">forward-in - 内网转发</option>
                    <option value="forward-out">forward-out - 外网转发</option>
                    <option value="mixed">mixed - 混合区域</option>
                  </select>
                  <button type="button" @click="addZone" class="btn-default btn-sm" :disabled="!newZoneType">添加区域</button>
                </div>
              </div>

              <!-- edge 区域模板 -->
              <div v-for="(zoneData, zoneType) in form.zones" :key="zoneType" class="mb-4 p-3 bg-gray-50 rounded-md">
                <template v-if="zoneType === 'edge'">
                  <div class="flex items-center justify-between mb-2">
                    <span class="font-medium text-sm text-gray-700">edge - 末端区域</span>
                    <button type="button" @click="removeZone(zoneType)" class="text-danger-500 hover:text-danger-700 text-sm">删除区域类型</button>
                  </div>
                  <div class="pl-3 space-y-3">
                    <div v-for="(zoneConfig, zoneName) in zoneData" :key="zoneName" class="bg-white p-2 rounded">
                      <div class="flex gap-2 items-center">
                        <div class="flex-1">
                          <label class="block text-xs text-gray-500 mb-0.5">区域名称</label>
                          <input v-model="zoneConfig._name" type="text" class="form-input text-xs" placeholder="如 Core_Server、PC" />
                        </div>
                        <div class="flex-[2]">
                          <label class="block text-xs text-gray-500 mb-0.5">直连网段 <span class="text-gray-400">（CIDR格式）</span></label>
                          <input v-model="zoneConfig._netsJson" type="text" class="form-input text-xs" placeholder='如 ["172.25.1.0/24", "172.26.1.0/24"]' />
                        </div>
                        <button type="button" @click="removeZoneDetail(zoneType, zoneName)" class="text-danger-500 text-xs px-2 mt-4">删除</button>
                      </div>
                    </div>
                    <button type="button" @click="addEdgeZone" class="text-primary-600 hover:text-primary-700 text-xs">+ 添加末端区域</button>
                  </div>
                </template>

                <template v-else-if="zoneType === 'forward-in' || zoneType === 'mixed'">
                  <div class="flex items-center justify-between mb-2">
                    <span class="font-medium text-sm text-gray-700">{{ zoneType }} - {{ zoneType === 'forward-in' ? '内网转发' : '混合区域' }}</span>
                    <button type="button" @click="removeZone(zoneType)" class="text-danger-500 hover:text-danger-700 text-sm">删除区域类型</button>
                  </div>
                  <div class="pl-3 space-y-2">
                    <div v-for="(zoneConfig, zoneName) in zoneData" :key="zoneName" class="bg-white p-2 rounded">
                      <div class="flex gap-2 items-center">
                        <div class="flex-1">
                          <label class="block text-xs text-gray-500 mb-0.5">区域名称</label>
                          <input v-model="zoneConfig._name" type="text" class="form-input text-xs" placeholder="如 untrust、trust" />
                        </div>
                        <div class="flex-1">
                          <label class="block text-xs text-gray-500 mb-0.5">关联网段 <span class="text-gray-400">（net）</span></label>
                          <input v-model="zoneConfig._netsJson" type="text" class="form-input text-xs" placeholder='如 ["0.0.0.0/0"]' />
                        </div>
                        <div class="flex-1">
                          <label class="block text-xs text-gray-500 mb-0.5">关联设备 <span class="text-gray-400">（dev）</span></label>
                          <input v-model="zoneConfig._devsJson" type="text" class="form-input text-xs" placeholder='如 ["USG6660"]' />
                        </div>
                        <button type="button" @click="removeZoneDetail(zoneType, zoneName)" class="text-danger-500 text-xs px-2 mt-4">删除</button>
                      </div>
                    </div>
                    <button type="button" @click="addZoneDetail(zoneType)" class="text-primary-600 hover:text-primary-700 text-xs">+ 添加区域详情</button>
                  </div>
                </template>

                <template v-else-if="zoneType === 'forward-out'">
                  <div class="flex items-center justify-between mb-2">
                    <span class="font-medium text-sm text-gray-700">forward-out - 外网转发</span>
                    <button type="button" @click="removeZone(zoneType)" class="text-danger-500 hover:text-danger-700 text-sm">删除区域类型</button>
                  </div>
                  <div class="pl-3 space-y-2">
                    <div v-for="(zoneConfig, zoneName) in zoneData" :key="zoneName" class="bg-white p-2 rounded">
                      <div class="flex gap-2 items-center">
                        <div class="flex-1">
                          <label class="block text-xs text-gray-500 mb-0.5">区域名称</label>
                          <input v-model="zoneConfig._name" type="text" class="form-input text-xs" placeholder="如 internet" />
                        </div>
                        <div class="flex-1">
                          <label class="block text-xs text-gray-500 mb-0.5">允许源 <span class="text-gray-400">（allow）</span></label>
                          <input v-model="zoneConfig._allowsJson" type="text" class="form-input text-xs" placeholder='如 ["5.5.1.0/24"]' />
                        </div>
                        <div class="flex-1">
                          <label class="block text-xs text-gray-500 mb-0.5">网段 <span class="text-gray-400">（net）</span></label>
                          <input v-model="zoneConfig._netsJson" type="text" class="form-input text-xs" placeholder='如 ["6.6.1.0/24"]' />
                        </div>
                        <button type="button" @click="removeZoneDetail(zoneType, zoneName)" class="text-danger-500 text-xs px-2 mt-4">删除</button>
                      </div>
                    </div>
                    <button type="button" @click="addZoneDetail(zoneType)" class="text-primary-600 hover:text-primary-700 text-xs">+ 添加区域详情</button>
                  </div>
                </template>
              </div>

              <div v-if="Object.keys(form.zones).length === 0" class="text-center text-sm text-gray-400 py-4">
                暂无区域配置，点击上方"添加区域"开始配置
              </div>
            </div>

            <div class="flex justify-end gap-3 pt-4">
              <button type="button" @click="goBack" class="btn-default">取消</button>
              <button type="submit" class="btn-primary" :disabled="submitting">{{ submitting ? '保存中...' : '保存配置' }}</button>
            </div>
          </form>

          <div v-if="message" :class="['mt-4 px-4 py-3 rounded-md text-sm', message.type === 'success' ? 'bg-success-50 text-success-700 border border-success-200' : 'bg-danger-50 text-danger-700 border border-danger-200']">
            {{ message.text }}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header"><h3 class="text-sm font-semibold text-gray-900">区域类型说明</h3></div>
        <div class="card-body">
          <ul class="space-y-3 text-sm text-gray-600">
            <li><code class="text-xs bg-gray-100 px-1 rounded">edge</code> - 末端区域，配置直连网段，<strong>支持多个区域</strong></li>
            <li><code class="text-xs bg-gray-100 px-1 rounded">forward-in</code> - 内网转发区域，关联网段或远端防火墙</li>
            <li><code class="text-xs bg-gray-100 px-1 rounded">forward-out</code> - 外网转发区域，连接互联网</li>
            <li><code class="text-xs bg-gray-100 px-1 rounded">mixed</code> - 混合区域，同时包含直连网段和远端防火墙</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { deviceAPI } from '../services/api'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.query.name)
const submitting = ref(false)
const message = ref('')
const newZoneType = ref('')

const form = reactive({
  name: '',
  vendor: 'huawei',
  ip: '',
  port: 22,
  username: '',
  password: '',
  location: '',
  description: '',
  zones: {}
})

const loadDevice = async (name) => {
  try {
    const r = await deviceAPI.get(name)
    if (r.data.device) {
      const d = r.data.device
      form.name = d.name
      form.vendor = d.vendor
      form.ip = d.ip
      form.port = d.port
      form.username = d.username || ''
      form.password = d.password || ''
      form.location = d.location || ''
      form.description = d.description || ''
      form.zones = parseZonesFromConfig(d.zones)
    }
  } catch (e) {
    message.value = { type: 'error', text: '加载设备失败：' + (e.message || '未知错误') }
  }
}

const parseZonesFromConfig = (zones) => {
  if (!zones) return {}
  const result = {}
  for (const [type, data] of Object.entries(zones)) {
    if (type === 'edge') {
      // edge 格式: {'aaa': ['1.1.1.0'], 'bbb': ['2.2.1.0']}
      result[type] = {}
      for (const [zoneName, nets] of Object.entries(data)) {
        result[type][`_edge_${zoneName}`] = {
          _name: zoneName,
          _netsJson: JSON.stringify(nets || [])
        }
      }
    } else if (type === 'forward-in' || type === 'mixed') {
      result[type] = {}
      for (const [name, config] of Object.entries(data)) {
        result[type][`_fi_${name}`] = {
          _name: name,
          _netsJson: JSON.stringify(config.net || []),
          _devsJson: JSON.stringify(config.dev || [])
        }
      }
    } else if (type === 'forward-out') {
      result[type] = {}
      for (const [name, config] of Object.entries(data)) {
        result[type][`_fo_${name}`] = {
          _name: name,
          _allowsJson: JSON.stringify(config.allow || []),
          _netsJson: JSON.stringify(config.net || [])
        }
      }
    }
  }
  return result
}

const buildZonesForSubmit = () => {
  const zones = {}
  for (const [type, data] of Object.entries(form.zones)) {
    if (type === 'edge') {
      // edge 格式: {'aaa': ['1.1.1.0'], 'bbb': ['2.2.1.0']}
      zones[type] = {}
      for (const [key, config] of Object.entries(data)) {
        const zoneName = config._name || key.replace('_edge_', '')
        const nets = JSON.parse(config._netsJson || '[]')
        if (zoneName) {
          zones[type][zoneName] = nets
        }
      }
    } else if (type === 'forward-in' || type === 'mixed') {
      zones[type] = {}
      for (const [key, config] of Object.entries(data)) {
        const realName = config._name || key.replace(/^_fi_/, '')
        zones[type][realName] = {
          net: JSON.parse(config._netsJson || '[]'),
          dev: JSON.parse(config._devsJson || '[]')
        }
      }
    } else if (type === 'forward-out') {
      zones[type] = {}
      for (const [key, config] of Object.entries(data)) {
        const realName = config._name || key.replace(/^_fo_/, '')
        zones[type][realName] = {
          allow: JSON.parse(config._allowsJson || '[]'),
          net: JSON.parse(config._netsJson || '[]')
        }
      }
    }
  }
  return zones
}

const addZone = () => {
  if (!newZoneType.value) return
  if (!form.zones[newZoneType.value]) {
    if (newZoneType.value === 'edge') {
      form.zones[newZoneType.value] = {}
      // 添加一个默认的 edge 区域
      addEdgeZone()
    } else {
      form.zones[newZoneType.value] = {}
    }
  }
  newZoneType.value = ''
}

const addEdgeZone = () => {
  const newName = `zone_${Date.now()}`
  form.zones.edge[`_edge_${newName}`] = { _name: newName, _netsJson: '[]' }
}

const removeZone = (type) => {
  delete form.zones[type]
}

const addZoneDetail = (type) => {
  const newName = `zone_${Date.now()}`
  if (type === 'forward-in' || type === 'mixed') {
    form.zones[type][`_fi_${newName}`] = { _name: newName, _netsJson: '[]', _devsJson: '[]' }
  } else if (type === 'forward-out') {
    form.zones[type][`_fo_${newName}`] = { _name: newName, _allowsJson: '[]', _netsJson: '[]' }
  }
}

const removeZoneDetail = (type, name) => {
  delete form.zones[type][name]
}

const handleSubmit = async () => {
  submitting.value = true
  message.value = ''
  try {
    const data = {
      name: form.name,
      vendor: form.vendor,
      ip: form.ip,
      port: form.port || 22,
      username: form.username,
      password: form.password,
      location: form.location,
      description: form.description,
      zones: buildZonesForSubmit()
    }

    let r
    if (isEdit.value) {
      r = await deviceAPI.update(form.name, data)
    } else {
      r = await deviceAPI.create(data)
    }

    if (r.data.status === 'success') {
      message.value = { type: 'success', text: r.data.message }
      setTimeout(() => router.push('/devices'), 1500)
    } else {
      message.value = { type: 'error', text: r.data.detail || '操作失败' }
    }
  } catch (e) {
    message.value = { type: 'error', text: '操作失败：' + (e.response?.data?.detail || e.message) }
  } finally {
    submitting.value = false
  }
}

const goBack = () => router.push('/devices')

onMounted(() => {
  if (isEdit.value) {
    loadDevice(route.query.name)
  }
})
</script>
