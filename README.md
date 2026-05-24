# 防火墙自动化运维平台

基于 Vue3 + FastAPI 的防火墙策略自动化运维平台，支持多厂商防火墙设备的策略生成、冲突检测、冗余分析和配置下发。

## 功能特性

### 核心功能
- **智能路径计算**：基于网络拓扑自动计算防火墙路径，生成跨设备的策略配置
- **CIDR 子网掩码支持**：路径计算引擎支持 CIDR 网段匹配（如 `10.0.0.0/8` 包含 `10.24.0.0/16`）
- **多 Edge 子区域**：支持在同一防火墙下配置多个末端区域（如 Core_Server、PC 各自独立区域）
- **配置文件驱动**：设备信息统一由配置文件管理，支持 Web 界面直接编辑
- **策略模拟验证**：策略下发前自动进行冲突检测和冗余分析
- **多厂商支持**：支持华为、山石、H3C、Juniper 等主流防火墙厂商
- **地址组/端口组管理**：集中管理地址组和端口组，支持批量配置下发
- **模拟模式**：无真实设备时可直接保存策略到数据库，便于测试和演示

### 前端特性
- Vue3 + Composition API
- Tailwind CSS 企业级 UI 设计
- 响应式布局，支持桌面端和平板设备
- 实时表单验证和状态反馈
- 策略脚本一键复制
- 表单数据自动保存到 sessionStorage

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- SQLite（默认数据库）

### 1. 安装后端依赖

```bash
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

### 数据存储架构

项目采用**配置文件 + 数据库**双存储架构，职责分明：

| 存储方式 | 位置 | 存储内容 |
|---------|------|---------|
| **配置文件** | `config/devices.py` | 防火墙设备信息（名称、厂商、IP、区域拓扑） |
| **SQLite 数据库** | `database/firewall_platform.db` | 地址组、端口组、安全策略、审计日志、组配置状态 |

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
├── main.py                     # 应用入口
├── api/                        # API 路由和请求模型
│   ├── routes.py               # RESTful API 路由（30+ 接口）
│   └── models.py               # Pydantic 请求模型
├── services/                   # 业务逻辑层
│   ├── path_engine.py          # 防火墙路径计算引擎（核心）
│   ├── policy_manager.py       # 策略管理器
│   ├── policy_validator.py     # 策略验证器（冲突检测、冗余分析）
│   ├── group_manager.py        # 地址组/端口组管理器
│   └── config_manager.py       # 配置文件读写管理器
├── config/                     # 配置文件
│   ├── devices.py              # 防火墙设备配置（数据源）
│   └── backups/                # 配置文件备份目录
├── database/                   # 数据访问层
│   └── models.py               # SQLAlchemy 数据模型
├── adapters/                   # 防火墙适配器（适配器模式）
│   ├── base.py                 # 适配器基类
│   ├── huawei.py               # 华为防火墙适配器
│   ├── hillstone.py            # 山石防火墙适配器
│   ├── h3c.py                  # H3C 防火墙适配器
│   └── juniper.py              # Juniper 防火墙适配器
├── factory/                    # 工厂模式
│   └── firewall_factory.py     # 防火墙工厂类
├── templates/                  # Jinja2 配置模板
│   ├── huawei_policy.j2
│   ├── hillstone_policy.j2
│   ├── h3c_policy.j2
│   ├── juniper_policy.j2
│   ├── address_group.j2
│   └── port_group.j2
├── frontend/                   # 前端应用
│   └── src/
│       ├── views/              # 页面组件
│       ├── services/           # API 服务
│       ├── router/             # 路由配置
│       └── assets/             # 样式资源
└── tests/                      # 单元测试
```

## 设备配置文件格式

设备信息统一维护在 `config/devices.py` 中，支持以下区域类型：

```python
firewall_devices = {
    'USG6660': {
        'name': 'USG6660',
        'vendor': 'huawei',
        'ip': '172.31.255.2',
        'zones': {
            'edge': {                          # 末端区域（直连网段）
                'Core_Server': ['172.25.1.0/24', '172.25.2.0/24'],
                'PC': ['172.27.1.0/24'],
            },
            'forward-in': {                    # 入方向转发区域
                'untrust': {
                    'net': ['0.0.0.0/0'],      # 网段列表
                    'dev': [],                  # 关联设备列表
                },
            },
            'forward-out': {                   # 出方向转发区域
                'untrust': {
                    'net': [],
                    'allow': ['172.28.32.0/24'],  # 允许网段
                },
            },
            'mixed': { ... },                  # 混合区域
        },
    },
}
```

### 区域类型说明

| 区域类型 | 说明 | 格式 |
|---------|------|------|
| `edge` | 末端区域，直连网段 | `{区域名: [CIDR列表]}` |
| `forward-in` | 入方向转发区域 | `{区域名: {net: [], dev: []}}` |
| `forward-out` | 出方向转发区域 | `{区域名: {net: [], allow: []}}` |
| `mixed` | 混合区域 | `{区域名: {net: [], dev: []}}` |

## API 接口说明

### 一、设备管理

| 方法 | 端点 | 功能 |
|------|------|------|
| POST | `/api/v1/devices/register` | 注册新设备 |
| GET | `/api/v1/devices` | 获取所有设备 |
| GET | `/api/v1/devices/{name}` | 获取单个设备 |
| DELETE | `/api/v1/devices/{name}` | 删除设备 |
| GET | `/api/v1/devices/{name}/heartbeat` | 检查设备心跳 |

### 二、配置文件管理

| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/api/v1/config/devices` | 获取所有设备配置 |
| GET | `/api/v1/config/devices/{name}` | 获取单个设备配置 |
| POST | `/api/v1/config/devices` | 新增设备配置 |
| PUT | `/api/v1/config/devices/{name}` | 更新设备配置 |
| DELETE | `/api/v1/config/devices/{name}` | 删除设备配置 |
| POST | `/api/v1/config/devices/backup` | 备份配置文件 |
| POST | `/api/v1/config/devices/validate` | 验证设备配置格式 |

#### 新增/更新设备配置请求体

```json
{
  "name": "USG6660",
  "vendor": "huawei",
  "ip": "172.31.255.2",
  "port": 22,
  "username": "",
  "password": "",
  "location": "",
  "zones": {
    "edge": {
      "Core_Server": ["172.25.1.0/24", "172.25.2.0/24"]
    },
    "forward-in": {
      "untrust": { "net": ["0.0.0.0/0"], "dev": [] }
    }
  }
}
```

### 三、策略管理

#### 3.1 生成策略
- **端点**: `POST /api/v1/policies/generate`
- **请求体**:
```json
{
  "policy_name": "web_https_access",
  "source_group": "web_servers",
  "dest_group": "app_servers",
  "port_group": "https_ports"
}
```

#### 3.2 模拟验证（dry_run）
- **端点**: `POST /api/v1/policies/generate?dry_run=true`
- 生成策略并进行冲突检测和冗余分析

#### 3.3 应用策略
- **端点**: `POST /api/v1/policies/apply?simulate=true`
- `simulate=true`（默认）：模拟模式，保存到数据库
- `simulate=false`：真实模式，SSH 连接设备下发

#### 3.4 策略验证
- **端点**: `POST /api/v1/policies/validate`
- 独立的冲突检测和冗余分析

#### 3.5 获取策略列表
- **端点**: `GET /api/v1/policies`

### 四、地址组管理

| 方法 | 端点 | 功能 |
|------|------|------|
| POST | `/api/v1/groups/address` | 创建地址组 |
| GET | `/api/v1/groups/address` | 获取所有地址组 |
| GET | `/api/v1/groups/address/{name}` | 获取地址组 |
| PUT | `/api/v1/groups/address/{name}` | 更新地址组 |
| DELETE | `/api/v1/groups/address/{name}` | 删除地址组 |
| POST | `/api/v1/groups/address/{name}/generate` | 生成配置脚本 |
| POST | `/api/v1/groups/address/{name}/apply/{device}` | 应用到指定设备 |
| POST | `/api/v1/groups/address/{name}/apply-all` | 批量应用 |
| GET | `/api/v1/groups/address/{name}/status` | 获取配置状态 |

### 五、端口组管理

与地址组接口结构相同，端点路径为 `/api/v1/groups/port/...`

## 路径计算引擎

### 核心流程

```
PathCalculator.__init__()
  ├── _build_direct_network_map()     # {网段 → {防火墙, 区域}}
  ├── _build_middle_forward_map()     # {防火墙 → {对端: [中间防火墙]}}
  └── _build_internet_forward_map()   # {防火墙 → 默认出接口区域}

PathCalculator.calculate_path(src_ip, dst_ip)
  ├── 查找源IP直连防火墙和区域
  ├── 查找目的IP直连防火墙和区域
  ├── 查找中间防火墙（递归，最大10跳）
  ├── 补全源/目的区域信息
  └── 返回完整路径 [{firewall, src_zone, dst_zone}, ...]
```

### CIDR 网段匹配

引擎使用 Python `ipaddress` 模块进行精确的网段包含判断：

- `"10.0.1.50"` in `"10.0.0.0/16"` → True
- `"10.24.0.0/16"` in `"10.0.0.0/8"` → True（网段包含）
- `"192.168.1.0/24"` in `"192.168.0.0/16"` → True

## 策略验证算法

### 冲突检测

**冲突条件**：匹配条件有重叠 **且** 动作相反（permit vs deny）

系统从四个维度比较规则：
- **源 IP 范围**：支持 CIDR 网段和 `any` 通配符
- **目的 IP 范围**：支持 CIDR 网段和 `any` 通配符
- **端口范围**：支持单个端口、范围（如 `80-443`）和 `any`
- **协议**：支持 tcp、udp、icmp 和 `any`

**重叠关系判定**：

| 关系 | 说明 |
|------|------|
| `exact` | 完全重叠（所有维度完全相等） |
| `new_subset` | 新规则是已有规则的子集 |
| `existing_subset` | 新规则包含已有规则 |
| `partial` | 部分重叠 |
| `none` | 无重叠 |

### 冗余检测

**冗余条件**：匹配条件有重叠 **且** 动作相同

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
      "desc": "与已存在规则 'permit tcp 192.168.1.0/24 -> 10.0.0.0/24 eq 80' 直接冲突"
    },
    {
      "rule_index": 1,
      "type": "redundancy",
      "severity": "warning",
      "existing_rule_id": 3,
      "desc": "该规则已被规则 'permit tcp 192.168.0.0/16 -> 10.0.0.0/8 eq 80' 完全覆盖"
    }
  ],
  "summary": "发现 1 个冲突，1 个冗余规则"
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
| status | VARCHAR(20) | 状态（online/offline） |

> 注意：区域配置（zones）已迁移到 `config/devices.py` 配置文件，不再存储在数据库中。

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

### address_groups / port_groups（地址组/端口组表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(100) | 组名（唯一） |
| description | VARCHAR(500) | 描述 |
| addresses/ports | JSON | 地址/端口列表 |
| protocol | VARCHAR(20) | 协议（仅端口组） |

### *_device_status（组配置状态表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| group_name | VARCHAR(100) | 组名称 |
| device_name | VARCHAR(100) | 设备名称 |
| status | VARCHAR(20) | 状态（pending/created） |
| config_script | TEXT | 配置脚本 |

## 使用示例

### 完整策略下发流程

```python
import requests

BASE_URL = "http://localhost:8080/api/v1"

# 1. 添加设备（写入配置文件）
device_data = {
    "name": "USG6660",
    "vendor": "huawei",
    "ip": "172.31.255.2",
    "zones": {
        "edge": {
            "Core_Server": ["172.25.1.0/24", "172.25.2.0/24"]
        },
        "forward-in": {
            "untrust": {"net": ["0.0.0.0/0"], "dev": []}
        }
    }
}
requests.post(f"{BASE_URL}/config/devices", json=device_data)

# 2. 创建地址组
requests.post(f"{BASE_URL}/groups/address", json={
    "name": "web_servers",
    "addresses": ["172.25.1.10", "172.25.1.11"],
    "description": "Web服务器"
})

# 3. 创建端口组
requests.post(f"{BASE_URL}/groups/port", json={
    "name": "https_ports",
    "ports": ["443", "8443"],
    "protocol": "tcp"
})

# 4. 生成策略（带模拟验证）
response = requests.post(f"{BASE_URL}/policies/generate?dry_run=true", json={
    "policy_name": "web_to_app_https",
    "source_group": "web_servers",
    "dest_group": "app_servers",
    "port_group": "https_ports"
})
result = response.json()

# 5. 应用策略（模拟模式）
for fw in result["data"]["firewall_policies"]:
    requests.post(f"{BASE_URL}/policies/apply?simulate=true", json={
        "policy_name": "web_to_app_https",
        "device_name": fw["device_name"],
        "policy_script": fw["policy_script"],
        "source_zone": fw["source_zone"],
        "dest_zone": fw["dest_zone"],
        "action": "permit"
    })
```

## 前端页面说明

| 页面 | 路径 | 功能 |
|------|------|------|
| 仪表盘 | `/` | 设备、策略统计信息 |
| 设备列表 | `/devices` | 管理防火墙设备（配置文件驱动） |
| 添加/编辑设备 | `/devices/register` | 编辑设备配置和区域信息 |
| 策略生成 | `/policies/generate` | 生成策略，查看防火墙路径 |
| 策略列表 | `/policies` | 查看已保存的策略 |
| 地址组列表 | `/groups/address` | 管理地址组 |
| 创建地址组 | `/groups/address/create` | 创建地址组 |
| 端口组列表 | `/groups/port` | 管理端口组 |
| 创建端口组 | `/groups/port/create` | 创建端口组 |

## 注意事项

1. **配置文件驱动**：设备信息存储在 `config/devices.py`，修改后自动备份到 `config/backups/`
2. **模拟模式**：策略应用默认为模拟模式，生产环境请设置 `simulate=false`
3. **策略验证**：建议正式下发前始终进行模拟验证，避免冲突
4. **设备心跳**：依赖 SSH 连接，确保防火墙的 SSH 服务已开启
5. **数据备份**：定期备份 SQLite 数据库文件和配置文件

## 测试

```bash
python -m pytest tests/test_policy_validator.py -v
```

## 许可证

MIT License
