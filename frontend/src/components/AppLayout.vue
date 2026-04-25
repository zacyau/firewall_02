<template>
  <div class="flex h-screen overflow-hidden">
    <aside
      :class="[
        'flex flex-col bg-white border-r border-gray-200 transition-all duration-200 z-30',
        collapsed ? 'w-16' : 'w-56',
        mobileOpen ? 'fixed inset-y-0 left-0' : 'hidden lg:flex',
      ]"
    >
      <div class="flex items-center h-14 px-4 border-b border-gray-100 shrink-0">
        <div class="flex items-center gap-2 overflow-hidden">
          <svg class="w-7 h-7 text-primary-500 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          <span v-if="!collapsed" class="text-base font-semibold text-gray-900 whitespace-nowrap">防火墙运维</span>
        </div>
      </div>

      <nav class="flex-1 py-3 overflow-y-auto">
        <ul class="space-y-0.5 px-2">
          <li v-for="item in menuItems" :key="item.path">
            <router-link
              :to="item.path"
              :class="[
                'flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors duration-100',
                isActive(item.path)
                  ? 'bg-primary-50 text-primary-600'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
              ]"
              @click="mobileOpen = false"
            >
              <component :is="item.icon" class="w-5 h-5 shrink-0" />
              <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
            </router-link>
          </li>
        </ul>
      </nav>

      <div class="hidden lg:flex items-center justify-center h-12 border-t border-gray-100 shrink-0">
        <button
          class="p-1.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
          @click="collapsed = !collapsed"
        >
          <svg :class="['w-4 h-4 transition-transform duration-200', collapsed && 'rotate-180']" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 19l-7-7 7-7M18 19l-7-7 7-7"/>
          </svg>
        </button>
      </div>
    </aside>

    <div v-if="mobileOpen" class="fixed inset-0 bg-black/30 z-20 lg:hidden" @click="mobileOpen = false" />

    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <header class="flex items-center justify-between h-14 px-6 bg-white border-b border-gray-200 shrink-0">
        <div class="flex items-center gap-3">
          <button class="lg:hidden p-1.5 -ml-1.5 rounded-md text-gray-500 hover:bg-gray-100" @click="mobileOpen = !mobileOpen">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 12h18M3 6h18M3 18h18"/>
            </svg>
          </button>
          <h2 class="text-base font-medium text-gray-800">{{ currentTitle }}</h2>
        </div>
        <div class="flex items-center gap-2 text-xs text-gray-400">
          <span>华为 / 山石 / 新华三 / 瞻博</span>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const collapsed = ref(false)
const mobileOpen = ref(false)

const IconDashboard = {
  render() {
    return h('svg', { class: 'w-5 h-5', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('rect', { x: '3', y: '3', width: '7', height: '7', rx: '1' }),
      h('rect', { x: '14', y: '3', width: '7', height: '7', rx: '1' }),
      h('rect', { x: '3', y: '14', width: '7', height: '7', rx: '1' }),
      h('rect', { x: '14', y: '14', width: '7', height: '7', rx: '1' }),
    ])
  },
}

const IconDevice = {
  render() {
    return h('svg', { class: 'w-5 h-5', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('rect', { x: '2', y: '3', width: '20', height: '14', rx: '2' }),
      h('path', { d: 'M8 21h8M12 17v4' }),
    ])
  },
}

const IconAddress = {
  render() {
    return h('svg', { class: 'w-5 h-5', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z' }),
      h('circle', { cx: '12', cy: '10', r: '3' }),
    ])
  },
}

const IconPort = {
  render() {
    return h('svg', { class: 'w-5 h-5', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5' }),
    ])
  },
}

const IconPolicy = {
  render() {
    return h('svg', { class: 'w-5 h-5', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z' }),
      h('path', { d: 'M14 2v6h6M16 13H8M16 17H8M10 9H8' }),
    ])
  },
}

const IconGenerate = {
  render() {
    return h('svg', { class: 'w-5 h-5', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M13 2L3 14h9l-1 8 10-12h-9l1-8z' }),
    ])
  },
}

const menuItems = [
  { path: '/', label: '控制台', icon: IconDashboard },
  { path: '/devices', label: '设备管理', icon: IconDevice },
  { path: '/groups/address', label: '地址组', icon: IconAddress },
  { path: '/groups/port', label: '端口组', icon: IconPort },
  { path: '/policies/generate', label: '策略生成', icon: IconGenerate },
  { path: '/policies', label: '策略列表', icon: IconPolicy },
]

const titleMap = {
  '/': '控制台',
  '/devices': '设备管理',
  '/devices/register': '注册设备',
  '/groups/address': '地址组管理',
  '/groups/address/create': '创建地址组',
  '/groups/port': '端口组管理',
  '/groups/port/create': '创建端口组',
  '/policies/generate': '策略生成',
  '/policies': '策略列表',
}

const currentTitle = computed(() => titleMap[route.path] || '防火墙运维平台')

const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>
