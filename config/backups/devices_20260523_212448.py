# 防火墙设备配置 - 统一配置格式
# 所有设备信息统一维护在此文件
#
# 生成时间: 2026-05-23 21:24:44

firewall_devices = {
    'FW_02': {
        'name': 'FW_02',
        'vendor': 'hillstone',
        'ip': '192.168.2.10',
        'port': 22,
        'username': 'admin',
        'password': 'admin123',
        'location': '数据中心B',
        'description': '汇聚防火墙',
        'zones': {
            'forward-in': {
                'to_aaa': {
                    'net': [],
                    'dev': ['FW_01'],
                },
                'to_ddd': {
                    'net': [],
                    'dev': ['FW_03', 'FW_04'],
                },
            },
        },
    },
    'FW_03': {
        'name': 'FW_03',
        'vendor': 'huawei',
        'ip': '192.168.3.10',
        'port': 22,
        'username': 'admin',
        'password': 'admin123',
        'location': '分支站点',
        'description': '分支防火墙03',
        'zones': {
            'edge': {
                'ddd': ['172.25.0.0'],
            },
            'forward-in': {
                'untrust': {
                    'net': ['0.0.0.0'],
                    'dev': [],
                },
            },
        },
    },
}

# 为了兼容旧代码，保留 DEVICES 别名指向 firewall_devices
DEVICES = firewall_devices