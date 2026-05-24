# 防火墙设备配置 - 统一配置格式
# 所有设备信息统一维护在此文件，数据库仅作为可选的辅助存储
#
# 配置结构说明:
#   - name: 防火墙名称（唯一标识）
#   - vendor: 厂商（huawei/hillstone/h3c/juniper）
#   - ip: 管理IP
#   - port: 管理端口（默认22）
#   - username/password: 登录凭据
#   - location: 位置描述
#   - zones: 安全区域配置
#
# 区域类型说明:
#   - edge: 末端区域，只配置直连网段
#   - forward-in: 内网转发区域，关联网段或远端防火墙
#   - forward-out: 外网转发区域，连接互联网
#   - mixed: 混合区域，同时包含直连网段和远端防火墙

firewall_devices = {
    'FW_01': {
        'name': 'FW_01',
        'vendor': 'huawei',
        'ip': '192.168.1.10',
        'port': 22,
        'username': 'admin',
        'password': 'admin123',
        'location': '数据中心A',
        'description': '核心防火墙',
        'zones': {
            'edge': {
                'aaa': ['1.1.1.0', '1.1.2.0', '1.1.3.0'],
                'bbb': ['2.2.1.0', '2.2.2.0'],
            },
            'forward-in': {
                'untrust': {
                    'net': ['0.0.0.0'],  # 默认区域，该墙所有edge区域与其他墙通信时必经
                    'dev': []
                }
            }
        }
    },
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
                'to_aaa': {'net': [], 'dev': ['FW_01']},
                'to_ddd': {'net': [], 'dev': ['FW_03', 'FW_04']},
            }
        }
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
                    'dev': []
                }
            }
        }
    },
    'FW_04': {
        'name': 'FW_04',
        'vendor': 'hillstone',
        'ip': '192.168.4.10',
        'port': 22,
        'username': 'admin',
        'password': 'admin123',
        'location': '分支站点',
        'description': '分支防火墙04',
        'zones': {
            'edge': {
                'eee': ['192.168.10.0'],
            },
            'forward-in': {
                'untrust': {
                    'net': ['0.0.0.0'],
                    'dev': []
                }
            }
        }
    },
    'FW_05': {
        'name': 'FW_05',
        'vendor': 'huawei',
        'ip': '192.168.5.10',
        'port': 22,
        'username': 'admin',
        'password': 'admin123',
        'location': '互联网出口',
        'description': '出口防火墙',
        'zones': {
            'forward-in': {
                'trust': {'net': ['5.5.1.0', '5.5.2.0'], 'dev': []},
            },
            'forward-out': {
                'dmz_1': {'allow': ['5.5.1.0'], 'net': ['6.6.1.0', '6.6.2.0']},
                'dmz_2': {'allow': ['5.5.2.0']},
            }
        }
    },
    'FW_07': {
        'name': 'FW_07',
        'vendor': 'h3c',
        'ip': '192.168.7.10',
        'port': 22,
        'username': 'admin',
        'password': 'admin123',
        'location': '混合区域',
        'description': '混合防火墙',
        'zones': {
            'mixed': {
                'eee': {'net': ['7.7.1.0'], 'dev': ['FW_08']},
                'fff': {'net': ['8.8.1.0'], 'dev': ['FW_09']},
            }
        }
    },
    'FW_08': {
        'name': 'FW_08',
        'vendor': 'juniper',
        'ip': '192.168.8.10',
        'port': 22,
        'username': 'admin',
        'password': 'admin123',
        'location': '远端站点',
        'description': '远端防火墙08',
        'zones': {
            'edge': {
                'net08': ['10.8.0.0'],
            }
        }
    },
    'FW_09': {
        'name': 'FW_09',
        'vendor': 'juniper',
        'ip': '192.168.9.10',
        'port': 22,
        'username': 'admin',
        'password': 'admin123',
        'location': '远端站点',
        'description': '远端防火墙09',
        'zones': {
            'edge': {
                'net09': ['10.9.0.0'],
            }
        }
    },
}

# 为了兼容旧代码，保留 DEVICES 别名指向 firewall_devices
DEVICES = firewall_devices
