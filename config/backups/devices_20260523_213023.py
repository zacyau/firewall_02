# 防火墙设备配置 - 统一配置格式
# 所有设备信息统一维护在此文件
#
# 生成时间: 2026-05-23 21:29:51

firewall_devices = {
    'USG6660': {
        'name': 'USG6660',
        'vendor': 'huawei',
        'ip': '172.31.255.2',
        'port': 22,
        'username': '',
        'password': '',
        'location': '',
        'description': '',
        'zones': {
            'edge': {
                '_netsJson': ['172.25.1.0', '172.26.1.0'],
            },
            'forward-in': {
                'untrust': {
                    'net': ['0.0.0.0'],
                    'dev': [],
                },
            },
        },
    },
    'K6680': {
        'name': 'K6680',
        'vendor': 'hillstone',
        'ip': '10.0.4.53',
        'port': 22,
        'username': '',
        'password': '',
        'location': '',
        'description': '',
        'zones': {
            'forward-in': {
                'LAN_CORE': {
                    'net': [],
                    'dev': ['USG6660'],
                },
                'Third_Party': {
                    'net': [],
                    'dev': ['USG6615E'],
                },
            },
        },
    },
}

# 为了兼容旧代码，保留 DEVICES 别名指向 firewall_devices
DEVICES = firewall_devices