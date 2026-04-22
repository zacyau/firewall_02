# 防火墙自动化运维平台

## 快速开始

### 1. 安装依赖

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

### 3. 访问API文档

打开浏览器访问：http://localhost:8080/docs

## API 接口说明

### 一、防火墙设备管理

#### 1.1 注册设备
- **端点**: `POST /api/v1/devices/register`
- **功能**: 注册新的防火墙设备
- **请求体**:
```json
{
  "name": "FW-01",
  "vendor": "huawei",
  "ip": "192.168.1.10",
  "port": 22,
  "username": "admin",
  "password": "admin123",
  "location": "数据中心A",
  "connected_networks": [
    {"network": "172.25.0.0/16", "zone": "trust", "interface": "G0/0"}
  ],
  "routing_table": [
    {"destination": "10.0.0.0/8", "next_hop": "FW-02", "zone": "untrust"}
  ]
}
```

#### 1.2 获取所有设备
- **端点**: `GET /api/v1/devices`
- **功能**: 获取所有注册的防火墙设备

#### 1.3 检查设备心跳
- **端点**: `GET /api/v1/devices/{device_name}/heartbeat`
- **功能**: 通过 SSH 连接检查防火墙状态

### 二、防火墙策略管理

#### 2.1 生成策略
- **端点**: `POST /api/v1/policies/generate`
- **功能**: 基于防火墙路径计算，自动生成策略脚本
- **请求体**:
```json
{
  "policy_name": "web_server_access",
  "source_ip": "10.0.1.100",
  "dest_ip": "10.0.2.200",
  "protocol": "tcp",
  "dest_port": "443"
}
```
- **响应**: 返回需要配置的防火墙列表及每个防火墙的策略脚本

#### 2.2 应用策略
- **端点**: `POST /api/v1/policies/apply`
- **功能**: 将策略脚本应用到指定的防火墙设备

## 架构设计

### 设计模式

1. **适配器模式 (Adapter Pattern)**
   - 统一不同厂商防火墙的接口
   - 每个厂商有独立的适配器类
   - 所有适配器继承自 `FirewallAdapter` 基类

2. **工厂模式 (Factory Pattern)**
   - `FirewallFactory` 负责创建不同厂商的适配器实例
   - 根据厂商名称自动选择对应的适配器

### 核心模块

1. **adapters/**: 适配器模块
   - `base.py`: 适配器基类定义统一接口
   - `huawei.py`: 华为防火墙适配器
   - `hillstone.py`: 山石防火墙适配器
   - `h3c.py`: 新华三防火墙适配器
   - `juniper.py`: 瞻博防火墙适配器

2. **factory/**: 工厂模块
   - `firewall_factory.py`: 防火墙工厂类

3. **services/**: 业务服务模块
   - `path_engine.py`: 防火墙路径计算引擎
   - `device_manager.py`: 设备管理器
   - `policy_manager.py`: 策略管理器
   - `config_loader.py`: 配置加载器（直接从数据库读取）

4. **database/**: 数据库模块
   - `models.py`: SQLAlchemy 数据模型

5. **config/**: 配置模块
   - `devices.py`: 设备配置字典

6. **templates/**: Jinja2 模板
   - 各厂商的策略配置模板

## 数据结构

### 路由表结构

```json
[
  {"destination": "172.25.0.0/16", "next_hop": "FW-01", "zone": "untrust"}
]
```

| 字段 | 说明 |
|------|------|
| destination | 目标网段 |
| next_hop | 下一跳防火墙名称 |
| zone | 区域名称 |

### 直连网段结构

```json
[
  {"network": "172.25.0.0/16", "zone": "trust", "interface": "G0/0"}
]
```

| 字段 | 说明 |
|------|------|
| network | 网段地址 |
| zone | 区域名称 |
| interface | 接口名称 |

## 使用示例

### 完整流程示例

```python
import requests

# 1. 注册设备
device_data = {
    "name": "FW-01",
    "vendor": "huawei",
    "ip": "192.168.1.10",
    "username": "admin",
    "password": "admin123",
    "connected_networks": [
        {"network": "172.25.0.0/16", "zone": "trust", "interface": "G0/0"}
    ],
    "routing_table": [
        {"destination": "10.0.0.0/8", "next_hop": "FW-02", "zone": "untrust"}
    ]
}
response = requests.post("http://localhost:8080/api/v1/devices/register", json=device_data)

# 2. 生成策略
policy_data = {
    "policy_name": "allow_https",
    "source_ip": "172.25.0.100",
    "dest_ip": "10.0.2.200",
    "protocol": "tcp",
    "dest_port": "443"
}
response = requests.post("http://localhost:8080/api/v1/policies/generate", json=policy_data)
print(response.json())

# 3. 应用策略到防火墙
apply_data = {
    "device_name": "FW-01",
    "policy_script": "生成的策略脚本"
}
response = requests.post("http://localhost:8080/api/v1/policies/apply", json=apply_data)
```

## 数据库表结构

1. **firewall_devices**: 防火墙设备表
2. **security_policies**: 安全策略表
3. **policy_audit_logs**: 策略审计日志表

## 注意事项

1. 策略应用前建议先在测试环境验证
2. 心跳检测依赖 SSH 连接，确保防火墙的 SSH 服务已开启
3. 默认使用 SQLite 数据库存储设备配置
4. 路由表中的 zone 字段用于策略生成时的源/目的 Zone 显示
