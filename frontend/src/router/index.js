import { createRouter, createWebHistory } from 'vue-router'
import DeviceList from '../views/DeviceList.vue'
import DeviceRegister from '../views/DeviceRegister.vue'
import PolicyGenerator from '../views/PolicyGenerator.vue'
import PolicyList from '../views/PolicyList.vue'
import Dashboard from '../views/Dashboard.vue'
import AddressGroupList from '../views/AddressGroupList.vue'
import AddressGroupCreate from '../views/AddressGroupCreate.vue'
import PortGroupList from '../views/PortGroupList.vue'
import PortGroupCreate from '../views/PortGroupCreate.vue'

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
  },
  {
    path: '/groups/address',
    name: 'AddressGroupList',
    component: AddressGroupList
  },
  {
    path: '/groups/address/create',
    name: 'AddressGroupCreate',
    component: AddressGroupCreate
  },
  {
    path: '/groups/port',
    name: 'PortGroupList',
    component: PortGroupList
  },
  {
    path: '/groups/port/create',
    name: 'PortGroupCreate',
    component: PortGroupCreate
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
