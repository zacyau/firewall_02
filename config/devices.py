# 防火墙设备配置 - 简化版
# 只包含：直连网段（含Zone信息）和路由表（不含metric）

DEVICES = {
    "huawei_fw_01": {
        "name": "huawei_fw_01",
        "vendor": "huawei",
        "ip": "192.168.1.10",
        "port": 22,
        "username": "admin",
        "password": "admin123",
        "location": "数据中心A",
        "connected_networks": [
            {"network": "192.168.145.0/24", "zone": "LAN_ACC", "interface": "GE0/0/1"},
            {"network": "192.168.1.0/24", "zone": "LAN_ACC", "interface": "GE0/0/0"}
        ],
        "routing_table": [
            {"destination": "172.25.0.0/16", "next_hop": "SZ-ACC-FW3800"},
            {"destination": "10.10.0.0/16", "next_hop": "hillstone_fw_01"}
        ]
    },
    "SZ-ACC-FW3800": {
        "name": "SZ-ACC-FW3800",
        "vendor": "hillstone",
        "ip": "192.168.2.10",
        "port": 22,
        "username": "admin",
        "password": "admin123",
        "location": "数据中心B",
        "connected_networks": [
            {"network": "172.25.200.0/24", "zone": "untrust", "interface": "ethernet0/2"},
            {"network": "172.25.0.0/16", "zone": "untrust", "interface": "ethernet0/2"},
            {"network": "192.168.2.0/24", "zone": "trust", "interface": "ethernet0/1"}
        ],
        "routing_table": [
            {"destination": "192.168.0.0/16", "next_hop": "huawei_fw_01"}
        ]
    },
    "hillstone_fw_01": {
        "name": "hillstone_fw_01",
        "vendor": "hillstone",
        "ip": "192.168.1.11",
        "port": 22,
        "username": "admin",
        "password": "admin123",
        "location": "数据中心A",
        "connected_networks": [
            {"network": "10.10.0.0/16", "zone": "dmz", "interface": "ethernet0/2"}
        ],
        "routing_table": []
    },
    "h3c_fw_01": {
        "name": "h3c_fw_01",
        "vendor": "h3c",
        "ip": "192.168.1.12",
        "port": 22,
        "username": "admin",
        "password": "admin123",
        "location": "数据中心B",
        "connected_networks": [],
        "routing_table": []
    },
    "juniper_fw_01": {
        "name": "juniper_fw_01",
        "vendor": "juniper",
        "ip": "192.168.1.13",
        "port": 22,
        "username": "admin",
        "password": "admin123",
        "location": "数据中心B",
        "connected_networks": [],
        "routing_table": []
    }
}
