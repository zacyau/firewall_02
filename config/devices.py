# 防火墙设备配置 - 统一配置格式
# 所有设备信息统一维护在此文件
#
# 生成时间: 2026-05-23 22:27:12

firewall_devices = {
    'USG6660': {
        'name': 'USG6660',
        'vendor': 'huawei',
        'ip': '1.1.1.1',
        'port': 22,
        'username': '',
        'password': '',
        'location': '',
        'description': '',
        'zones': {
            'edge': {
                'Core_Server': ['172.25.1.0/24', '172.25.2.0/24'],
                'PC': ['172.27.1.0/24'],
            },
            'forward-in': {
                'untrust': {
                    'net': ['0.0.0.0/0'],
                    'dev': [],
                },
            },
        },
    },
    'K6680': {
        'name': 'K6680',
        'vendor': 'hillstone',
        'ip': '2.2.2.2',
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
            'edge': {
                'WAN': ['10.0.0.0/8'],
            },
        },
    },
    'USG6615E': {
        'name': 'USG6615E',
        'vendor': 'huawei',
        'ip': '10.0.5.91',
        'port': 22,
        'username': '',
        'password': '',
        'location': '',
        'description': '',
        'zones': {
            'forward-in': {
                'trust': {
                    'net': [],
                    'dev': ['USG6660', 'K6680'],
                },
            },
            'edge': {
                'untrust': ['129.1.0.0/16'],
            },
        },
    },
    'A3800': {
        'name': 'A3800',
        'vendor': 'hillstone',
        'ip': '3.3.3.3',
        'port': 22,
        'username': '',
        'password': '',
        'location': '',
        'description': '',
        'zones': {
            'forward-in': {
                'trust': {
                    'net': [],
                    'dev': ['USG6660', 'K6680'],
                },
            },
            'forward-out': {
                'untrust': {
                    'net': [],
                    'allow': ['172.28.32.0/24'],
                },
            },
        },
    },
}