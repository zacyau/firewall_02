<template>
  <div id="app">
    <nav class="navbar">
      <div class="navbar-brand">
        <h1>🛡️ 防火墙自动化运维平台</h1>
      </div>
      <div class="navbar-menu">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/devices" class="nav-link">设备管理</router-link>
        <router-link to="/groups/address" class="nav-link">地址组</router-link>
        <router-link to="/groups/port" class="nav-link">端口组</router-link>
        <router-link to="/policies/generate" class="nav-link">策略生成</router-link>
        <router-link to="/policies" class="nav-link">策略列表</router-link>
      </div>
    </nav>
    
    <main class="main-content">
      <router-view />
    </main>
    
    <footer class="footer">
      <p>&copy; 2026 防火墙自动化运维平台 - 支持华为/山石/新华三/瞻博防火墙</p>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.navbar {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar-brand h1 {
  font-size: 20px;
  font-weight: 600;
  color: #1890ff;
  margin: 0;
}

.navbar-menu {
  display: flex;
  gap: 8px;
}

.nav-link {
  padding: 16px 16px;
  color: #666;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s;
  border-bottom: 3px solid transparent;
}

.nav-link:hover {
  color: #1890ff;
  background: #f5f7fa;
}

.nav-link.router-link-active {
  color: #1890ff;
  border-bottom-color: #1890ff;
}

.main-content {
  min-height: calc(100vh - 140px);
  padding: 24px;
}

.footer {
  background: white;
  padding: 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
  border-top: 1px solid #e8e8e8;
}

@media (max-width: 768px) {
  .navbar-menu {
    flex-direction: column;
    gap: 0;
  }
  
  .nav-link {
    padding: 12px 16px;
    border-bottom: 1px solid #e8e8e8;
    border-left: 3px solid transparent;
  }
  
  .nav-link.router-link-active {
    border-left-color: #1890ff;
    border-bottom-color: #e8e8e8;
  }
}
</style>
