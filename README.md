# 防火墙自动化运维平台

基于 Vue3 + FastAPI 的防火墙策略自动化运维平台，支持多厂商防火墙设备的策略生成、冲突检测、冗余分析和配置下发。

## 功能特性

### 核心功能
- **智能路径计算**：基于网络拓扑自动计算防火墙路径，生成跨设备的策略配置
- **策略模拟验证**：策略下发前自动进行冲突检测和冗余分析
- **多厂商支持**：支持华为、山石、H3C、Juniper 等主流防火墙厂商
- **地址组/端口组管理**：集中管理地址组和端口组，支持批量配置下发
- **模拟模式**：无真实设备时可直接保存策略到数据库，便于测试和演示
- **数据持久化**：表单数据自动保存到 sessionStorage，刷新页面不丢失

### 前端特性
- Vue3 + Composition API
- Tailwind CSS 企业级 UI 设计
- 响应式布局，支持桌面端和平板设备
- 实时表单验证和状态反馈
- 策略脚本一键复制

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- SQLite（默认数据库）

### 1. 安装后端依赖

```bash
cd /Users/bobyau/Desktop/Zac/codes/Trae/firewall_02
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动前端服务

```bash
npm run dev
```

### 5. 访问系统

- 前端页面：http://localhost:3000
- API 文档：http://localhost:8080/docs

## 系统架构

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3 + Vite + Tailwind CSS + Axios |
| 后端 | FastAPI + SQLAlchemy + Pydantic |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） |
| 模板引擎 | Jinja2 |

### 核心模块

```
firewall_02/
├── api/                    # API 路由和请求模型
│   ├── routes.py          # RESTful API 路由
│   └── models.py          # Pydantic 请求/响应模型
├── services/              # 业务逻辑层
│   ├── path_engine.py     # 防火墙路径计算引擎
│   ├── policy_manager.py  # 策略管理器
│   ├── policy_validator.py # 策略验证器（冲突检测、冗余分析）
│   ├── device_manager.py  # 设备管理器
│   ├── group_manager.py   # 地址组/端口组管理器
│   └── template_renderer.py # 模板渲染器
├── database/              # 数据访问层
│   └── models.py          # SQLAlchemy 数据模型
├── adapters/              # 防火墙适配器（适配器模式）
│   ├── base.py           # 适配器基类
│   ├── huawei.py         # 华为防火墙适配器
│   ├── hillstone.py      # 山石防火墙适配器
│   ├── h3c.py           # H3C 防火墙适配器
│   └── juniper.py       # Juniper 防火墙适配器
├── factory/               # 工厂模式
│   └── firewall_factory.py # 防火墙工厂类
├── templates/             # Jinja2 配置模板
│   ├── huawei_policy.j2
│   ├── hillstone_policy.j2
│   └── ...
├── frontend/              # 前端应用
│   ├── src/
│   │   ├── views/        # 页面组件
│   │   ├── services/     # API 服务
│   │   └── assets/       # 样式资源
│   └── vite.config.js
└── tests/                 # 单元测试
```

## API 接口说明

### 一、防火墙设备管理

#### 1.1 注册设备
- **端点**: `POST /api/v1/devices/register`
- **功能**: 注册新的防火墙设备
- **请求体**:
```json
{
  "name": "huawei_fw_01",
  "vendor": "huawei",
  "ip": "192.168.1.10",
  "port": 22,
  "username": "admin",
  "password": "admin123",
  "location": "数据中心A",
  "connected_networks": [
    {"network": "192.168.145.0/24", "zone": "LAN_ACC", "interface": "GE0/0/1"}
  ],
  "routing_table": [
    {"destination": "172.25.0.0/16", "next_hop": "SZ-ACC-FW3800"}
  ]
}
```

#### 1.2 获取所有设备
- **端点**: `GET /api/v1/devices`
- **功能**: 获取所有注册的防火墙设备

#### 1.3 检查设备心跳
- **端点**: `GET /api/v1/devices/{device_name}/heartbeat`
- **功能**: 通过 SSH 连接检查防火墙状态

#### 1.4 删除设备
- **端点**: `DELETE /api/v1/devices/{device_name}`
- **功能**: 删除指定的防火墙设备

### 二、防火墙策略管理

#### 2.1 生成策略
- **端点**: `POST /api/v1/policies/generate`
- **功能**: 基于防火墙路径计算，自动生成策略脚本
- **请求体**:
```json
{
  "policy_name": "web_https_access",
  "source_group": "web_servers",
  "dest_group": "app_servers",
  "port_group": "https_ports",
  "description": "Web服务器访问应用服务器"
}
```
- **响应**: 返回需要配置的防火墙列表及每个防火墙的策略脚本

#### 2.2 模拟验证（dry_run）
- **端点**: `POST /api/v1/policies/generate?dry_run=true`
- **功能**: 生成策略并进行冲突检测和冗余分析，不保存到数据库
- **响应**: 包含验证报告，显示冲突和冗余情况

#### 2.3 应用策略
- **端点**: `POST /api/v1/policies/apply?simulate=true`
- **功能**: 将策略脚本应用到指定的防火墙设备
- **参数**:
  - `simulate=true`（默认）：模拟模式，直接保存到数据库，不连接真实设备
  - `simulate=false`：真实模式，连接防火墙设备并下发配置
- **请求体**:
```json
{
  "policy_name": "web_https_access",
  "device_name": "huawei_fw_01",
  "policy_script": "生成的策略脚本",
  "source_ip": "192.168.1.0/24",
  "dest_ip": "10.0.0.0/24",
  "protocol": "tcp",
  "dest_port": "443",
  "source_zone": "LAN_ACC",
  "dest_zone": "DMZ",
  "action": "permit"
}
```

#### 2.4 策略验证
- **端点**: `POST /api/v1/policies/validate`
- **功能**: 对策略规则进行独立的冲突检测和冗余分析
- **请求体**:
```json
{
  "device_id": "huawei_fw_01",
  "direction": "inbound",
  "rules": [
    {
      "source_ip": "192.168.1.0/24",
      "dest_ip": "10.0.0.0/24",
      "protocol": "tcp",
      "dest_port": "443",
      "action": "permit"
    }
  ]
}
```

#### 2.5 获取策略列表
- **端点**: `GET /api/v1/policies`
- **功能**: 获取所有已保存的策略

### 三、地址组管理

#### 3.1 创建地址组
- **端点**: `POST /api/v1/groups/address`
- **请求体**:
```json
{
  "name": "web_servers",
  "description": "Web服务器地址组",
  "addresses": ["192.168.1.10", "192.168.1.11"]
}
```

#### 3.2 获取地址组列表
- **端点**: `GET /api/v1/groups/address`

#### 3.3 生成地址组配置
- **端点**: `POST /api/v1/groups/address/{group_name}/generate`
- **功能**: 生成地址组在所有防火墙上的配置脚本

#### 3.4 应用地址组配置
- **端点**: `POST /api/v1/groups/address/{group_name}/apply/{device_name}`
- **功能**: 应用地址组配置到指定防火墙

#### 3.5 批量应用地址组
- **端点**: `POST /api/v1/groups/address/{group_name}/apply-all`
- **功能**: 批量应用到所有未配置的防火墙

#### 3.6 获取配置状态
- **端点**: `GET /api/v1/groups/address/{group_name}/status`
- **功能**: 获取地址组在各防火墙上的配置状态

### 四、端口组管理

#### 4.1 创建端口组
- **端点**: `POST /api/v1/groups/port`
- **请求体**:
```json
{
  "name": "https_ports",
  "description": "HTTPS端口组",
  "ports": ["443", "8443"],
  "protocol": "tcp"
}
```

#### 4.2-4.6 其他端口组接口
- 与地址组接口类似，端点路径为 `/groups/port/...`

## 策略验证算法

### 冲突检测

**冲突条件**：匹配条件有重叠 **且** 动作相反（permit vs deny）

系统从四个维度比较规则：
- **源 IP 范围**：支持 CIDR 网段和 `any` 通配符
- **目的 IP 范围**：支持 CIDR 网段和 `any` 通配符
- **端口范围**：支持单个端口、范围（如 `80-443`）和 `any`
- **协议**：支持 tcp、udp、icmp 和 `any`

**重叠关系判定**：
```
"exact"           - 完全重叠（所有维度完全相等）
"new_subset"      - 新规则是已有规则的子集
"existing_subset" - 新规则包含已有规则
"partial"         - 部分重叠
"none"            - 无重叠
```

**冲突类型**：
- **完全冲突**：匹配条件完全相同，动作相反
- **部分冲突**：匹配范围有包含关系，动作相反

### 冗余检测

**冗余条件**：匹配条件有重叠 **且** 动作相同

**冗余类型**：
- **完全冗余**：规则完全重复
- **子集冗余**：新规则被已有规则完全覆盖，可以移除

### 验证报告示例

```json
{
  "valid": false,
  "issues": [
    {
      "rule_index": 0,
      "type": "conflict",
      "severity": "error",
      "existing_rule_id": 5,
      "desc": "与已存在规则 'permit tcp 192.168.1.0/24 -> 10.0.0.0/24 eq 80' 直接冲突（匹配条件完全重叠，动作相反）"
    },
    {
      "rule_index": 1,
      "type": "redundancy",
      "severity": "warning",
      "existing_rule_id": 3,
      "desc": "该规则已被规则 'permit tcp 192.168.0.0/16 -> 10.0.0.0/8 eq 80' 完全覆盖，可以移除"
    }
  ],
  "summary": "发现 1 个冲突，1 个冗余规则",
  "device_reports": {
    "huawei_fw_01": {
      "valid": false,
      "summary": "发现 1 个冲突",
      "issues": [...]
    }
  }
}
```

## 数据库表结构

### firewall_devices（防火墙设备表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 设备名称（唯一） |
| vendor | VARCHAR(50) | 厂商（huawei/hillstone/h3c/juniper） |
| ip | VARCHAR(50) | 管理 IP |
| port | INTEGER | SSH 端口（默认 22） |
| username | VARCHAR(50) | 用户名 |
| password | VARCHAR(200) | 密码 |
| connected_networks | JSON | 直连网段及 Zone 信息 |
| routing_table | JSON | 路由表 |
| zone_mappings | JSON | Zone 映射配置 |
| status | VARCHAR(20) | 状态（online/offline） |

### security_policies（安全策略表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| policy_name | VARCHAR(100) | 策略名称 |
| source_ip | VARCHAR(50) | 源 IP |
| dest_ip | VARCHAR(50) | 目的 IP |
| protocol | VARCHAR(10) | 协议 |
| dest_port | VARCHAR(50) | 目的端口 |
| action | VARCHAR(20) | 动作（permit/deny） |
| source_zone | VARCHAR(50) | 源 Zone |
| dest_zone | VARCHAR(50) | 目的 Zone |
| device_name | VARCHAR(100) | 设备名称 |
| policy_script | TEXT | 策略脚本 |
| status | VARCHAR(20) | 状态（pending/applying/applied/failed） |
| error_message | TEXT | 错误信息 |

### address_groups（地址组表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 组名（唯一） |
| description | VARCHAR(500) | 描述 |
| addresses | JSON | IP 地址列表 |

### port_groups（端口组表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 组名（唯一） |
| description | VARCHAR(500) | 描述 |
| ports | JSON | 端口列表 |
| protocol | VARCHAR(20) | 协议（tcp/udp） |

### address_group_device_status（地址组设备状态表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| group_name | VARCHAR(100) | 地址组名称 |
| device_name | VARCHAR(100) | 设备名称 |
| status | VARCHAR(20) | 状态（pending/applied） |
| config_script | TEXT | 配置脚本 |

## 使用示例

### 完整策略下发流程

```python
import requests

BASE_URL = "http://localhost:8080/api/v1"

# 1. 注册设备
device_data = {
    "name": "huawei_fw_01",
    "vendor": "huawei",
    "ip": "192.168.1.10",
    "username": "admin",
    "password": "admin123",
    "connected_networks": [
        {"network": "192.168.145.0/24", "zone": "LAN_ACC", "interface": "GE0/0/1"}
    ],
    "routing_table": [
        {"destination": "172.25.0.0/16", "next_hop": "SZ-ACC-FW3800"}
    ]
}
requests.post(f"{BASE_URL}/devices/register", json=device_data)

# 2. 创建地址组
address_group = {
    "name": "web_servers",
    "addresses": ["192.168.145.10", "192.168.145.11"],
    "description": "Web服务器"
}
requests.post(f"{BASE_URL}/groups/address", json=address_group)

# 3. 创建端口组
port_group = {
    "name": "https_ports",
    "ports": ["443", "8443"],
    "protocol": "tcp",
    "description": "HTTPS端口"
}
requests.post(f"{BASE_URL}/groups/port", json=port_group)

# 4. 生成策略（带模拟验证）
policy_data = {
    "policy_name": "web_to_app_https",
    "source_group": "web_servers",
    "dest_group": "app_servers",
    "port_group": "https_ports"
}
response = requests.post(f"{BASE_URL}/policies/generate?dry_run=true", json=policy_data)
result = response.json()

# 检查验证报告
if result["data"]["validation"]["valid"]:
    print("验证通过，无冲突")
else:
    print("发现问题:", result["data"]["validation"]["summary"])

# 5. 应用策略（模拟模式）
for fw in result["data"]["firewall_policies"]:
    apply_data = {
        "policy_name": "web_to_app_https",
        "device_name": fw["device_name"],
        "policy_script": fw["policy_script"],
        "source_zone": fw["source_zone"],
        "dest_zone": fw["dest_zone"],
        "action": "permit"
    }
    requests.post(f"{BASE_URL}/policies/apply?simulate=true", json=apply_data)
```

## 前端页面说明

### 主要页面

| 页面 | 路径 | 功能 |
|------|------|------|
| 仪表盘 | `/` | 显示设备、策略、地址组统计信息 |
| 策略生成 | `/policy/generate` | 生成防火墙策略，支持模拟验证 |
| 策略列表 | `/policies` | 查看所有已保存的策略 |
| 设备列表 | `/devices` | 管理防火墙设备 |
| 设备注册 | `/devices/register` | 注册新设备 |
| 地址组列表 | `/groups/address` | 管理地址组 |
| 地址组创建 | `/groups/address/create` | 创建地址组 |
| 端口组列表 | `/groups/port` | 管理端口组 |
| 端口组创建 | `/groups/port/create` | 创建端口组 |

### 策略生成页面功能

1. **表单输入**：策略名称、源地址组、目的地址组、端口组、描述
2. **实时保存**：表单数据自动保存到 sessionStorage，刷新不丢失
3. **模拟验证**：生成策略前进行冲突检测和冗余分析
4. **路径展示**：显示防火墙路径及 Zone 配置信息
5. **脚本预览**：生成各厂商的配置脚本
6. **模拟模式**：无真实设备时直接保存到数据库
7. **状态跟踪**：显示策略应用状态（待下发/下发中/已应用/失败）

## 注意事项

1. **模拟模式**：默认开启，适用于测试环境。生产环境请关闭模拟模式（`simulate=false`）
2. **策略验证**：建议正式下发前始终进行模拟验证，避免冲突
3. **设备心跳**：依赖 SSH 连接，确保防火墙的 SSH 服务已开启
4. **数据备份**：定期备份 SQLite 数据库文件
5. **会话存储**：表单数据保存在浏览器 sessionStorage 中，关闭标签页后清除

## 测试

运行单元测试：

```bash
python -m pytest tests/test_policy_validator.py -v
```

## 许可证

MIT License
