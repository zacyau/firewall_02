# 多品牌防火墙Zone配置示例

## 场景说明

在实际环境中，不同厂商的防火墙Zone命名差异很大，例如：

| 厂商 | 源Zone | 目的Zone |
|------|--------|----------|
| 华为 | LAN_ACC | LAN_CORE |
| 山石 | trust | untrust |
| 新华三 | local | trust |
| 瞻博 | Trust | Untrust |

## 你的需求示例

**源IP**: 192.168.145.11
**目的IP**: 172.25.20.11
**A防火墙（华为）**: LAN_ACC → LAN_CORE
**B防火墙（山石）**: trust → untrust

## 解决方案

### 1. 配置文件 - 每台防火墙独立Zone映射

```python
DEVICES = {
    "huawei_fw_01": {
        "name": "huawei_fw_01",
        "vendor": "huawei",
        "ip": "192.168.1.10",
        "zone_mappings": {
            # 华为防火墙的Zone命名
            "LAN_ACC": ["192.168.0.0/16"],      # 接入层区域（源IP在此）
            "LAN_CORE": ["172.25.0.0/16"],      # 核心层区域（目的IP在此）
            "DMZ": ["10.10.0.0/16"],
            "WAN": ["0.0.0.0/0"]
        }
    },
    "hillstone_fw_01": {
        "name": "hillstone_fw_01",
        "vendor": "hillstone",
        "ip": "192.168.1.11",
        "zone_mappings": {
            # 山石防火墙的Zone命名
            "trust": ["192.168.0.0/16"],        # 信任区域（源IP在此）
            "untrust": ["172.25.0.0/16"],      # 非信任区域（目的IP在此）
            "dmz": ["10.10.0.0/16"],
            "wan": ["0.0.0.0/0"]
        }
    }
}
```

### 2. 路径计算引擎 - 智能Zone判断

系统会根据每台防火墙的独立Zone配置，自动判断：

```
源IP: 192.168.145.11
目的IP: 172.25.20.11

↓ 流量路径计算

防火墙1: huawei_fw_01 (华为)
  ├─ 源Zone: LAN_ACC (因为192.168.145.11在192.168.0.0/16范围内)
  └─ 目的Zone: LAN_CORE (因为172.25.20.11在172.25.0.0/16范围内)

防火墙2: hillstone_fw_01 (山石)
  ├─ 源Zone: trust (因为192.168.145.11在192.168.0.0/16范围内)
  └─ 目的Zone: untrust (因为172.25.20.11在172.25.0.0/16范围内)
```

### 3. 生成的CLI脚本

#### 华为防火墙脚本 (huawei_fw_01)
```bash
# 华为防火墙安全策略配置
# 策略名称: web_access_huawei_fw_01
# 源区域: LAN_ACC -> 目的区域: LAN_CORE

system-view
security-policy
 rule name web_access_huawei_fw_01
  source-zone LAN_ACC
  destination-zone LAN_CORE
  source-address 192.168.145.11
  destination-address 172.25.20.11
  service TCP destination-port 443
  action permit
 quit
quit
commit
```

#### 山石防火墙脚本 (hillstone_fw_01)
```bash
# 山石防火墙安全策略配置
# 策略名称: web_access_hillstone_fw_01
# 源区域: trust -> 目的区域: untrust

configure terminal
security-policy
 rule name web_access_hillstone_fw_01
  source-zone trust
  destination-zone untrust
  source-address 192.168.145.11
  destination-address 172.25.20.11
  service TCP destination-port 443
  action accept
 exit
exit
write memory
```

## 前端界面展示

### 防火墙路径可视化

```
┌─────────────────────────────────────────────────────────┐
│ 🛤️ 防火墙路径及Zone配置                                 │
├─────────────────────────────────────────────────────────┤
│ 路径摘要：                                              │
│ huawei_fw_01 (LAN_ACC → LAN_CORE) |                     │
│ hillstone_fw_01 (trust → untrust)                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────┐                                               │
│  │  1   │ 入口                                         │
│  │ huawei_fw_01 🔵                                      │
│  │ 华为  │                                              │
│  └──────┘                                               │
│                                                         │
│  源Zone: LAN_ACC (接入层区域)                           │
│     ↓                                                   │
│  目的Zone: LAN_CORE (核心层区域)                        │
│                                                         │
│  源IP: 192.168.145.11 → 目的IP: 172.25.20.11            │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                 ↓ 流量经过                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────┐                                               │
│  │  2   │ 出口                                         │
│  │ hillstone_fw_01 🟠                                   │
│  │ 山石  │                                              │
│  └──────┘                                               │
│                                                         │
│  源Zone: trust (信任区域)                               │
│     ↓                                                   │
│  目的Zone: untrust (非信任区域)                         │
│                                                         │
│  源IP: 192.168.145.11 → 目的IP: 172.25.20.11            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 核心优势

### ✅ 1. 厂商无关性
- 不需要为每个厂商硬编码Zone名称
- 每个防火墙独立配置自己的Zone命名
- 新增厂商只需添加适配器，无需修改逻辑

### ✅ 2. 智能Zone判断
- 根据IP自动匹配Zone
- 支持精确的CIDR范围配置
- 自动识别流量方向（入口/出口/中转）

### ✅ 3. 统一管理
- 所有防火墙统一配置管理
- 自动生成符合厂商CLI语法的脚本
- 可视化展示每台防火墙的Zone配置

## 配置说明

### Zone命名规范

建议遵循以下规范：

```python
# 标准Zone命名
"trust"        # 信任区域
"untrust"      # 非信任区域
"dmz"          # 隔离区
"local"        # 本地区域

# 华为特色
"LAN_ACC"      # 接入层
"LAN_CORE"     # 核心层
"WAN"          # 广域网

# 瞻博特色（首字母大写）
"Trust"        # 信任区域
"Untrust"      # 非信任区域
"DMZ"          # 隔离区
"Internet"     # 互联网
```

### IP范围配置

```python
# 单个IP
"192.168.1.100/32"

# 子网
"192.168.0.0/16"

# 多个子网
"192.168.0.0/16",
"172.25.0.0/16"
```

## 测试验证

### API测试

```bash
curl -X POST "http://localhost:8080/api/v1/policies/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_name": "web_access",
    "source_ip": "192.168.145.11",
    "dest_ip": "172.25.20.11",
    "protocol": "tcp",
    "dest_port": "443"
  }'
```

### 响应示例

```json
{
  "status": "success",
  "data": {
    "source_ip": "192.168.145.11",
    "dest_ip": "172.25.20.11",
    "protocol": "tcp",
    "dest_port": "443",
    "policy_name": "web_access",
    "firewall_count": 2,
    "firewall_policies": [
      {
        "device_name": "huawei_fw_01",
        "vendor": "huawei",
        "source_zone": "LAN_ACC",
        "dest_zone": "LAN_CORE",
        "source_zone_description": "接入层区域",
        "dest_zone_description": "核心层区域",
        "flow_direction": "入口",
        "sequence": 1,
        "policy_script": "# 华为防火墙CLI..."
      },
      {
        "device_name": "hillstone_fw_01",
        "vendor": "hillstone",
        "source_zone": "trust",
        "dest_zone": "untrust",
        "source_zone_description": "信任区域",
        "dest_zone_description": "非信任区域",
        "flow_direction": "出口",
        "sequence": 2,
        "policy_script": "# 山石防火墙CLI..."
      }
    ],
    "path_description": "huawei_fw_01 → hillstone_fw_01",
    "path_summary": "huawei_fw_01 (LAN_ACC → LAN_CORE) | hillstone_fw_01 (trust → untrust)"
  }
}
```

## 前端演示

访问 http://localhost:3000/policies/generate

1. 填写表单：
   - 策略名称：`web_access`
   - 源IP：`192.168.145.11`
   - 目的IP：`172.25.20.11`
   - 协议：`TCP`
   - 端口：`443`

2. 点击"⚡ 生成策略"

3. 查看可视化路径：
   - 每个防火墙显示自己的Zone命名
   - 包含Zone的中文描述
   - 标明流量方向（入口/出口/中转）

4. 审核并应用：
   - 查看每台防火墙的CLI脚本
   - 确认Zone配置正确
   - 点击"🚀 应用到防火墙"下发配置

---

**完美解决多厂商Zone命名不一致的问题！** 🎉
