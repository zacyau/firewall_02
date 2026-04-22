import { createRouter, createWebHistory } from 'vue-router'
import DeviceList from '../views/DeviceList.vue'
import DeviceRegister from '../views/DeviceRegister.vue'
import PolicyGenerator from '../views/PolicyGenerator.vue'
import PolicyList from '../views/PolicyList.vue'
import Dashboard from '../views/Dashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/devices',
    name: 'DeviceList',
    component: DeviceList
  },
  {
    path: '/devices/register',
    name: 'DeviceRegister',
    component: DeviceRegister
  },
  {
    path: '/policies/generate',
    name: 'PolicyGenerator',
    component: PolicyGenerator
  },
  {
    path: '/policies',
    name: 'PolicyList',
    component: PolicyList
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
