# 配置文件管理器 - 支持读写 config/devices.py
import os
import shutil
from datetime import datetime
from typing import Dict, Any, Optional

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE_PATH = os.path.join(PROJECT_ROOT, 'config', 'devices.py')
BACKUP_DIR = os.path.join(PROJECT_ROOT, 'config', 'backups')


class ConfigManager:
    """配置文件管理器"""

    def __init__(self):
        self.config_file = CONFIG_FILE_PATH
        self.backup_dir = BACKUP_DIR
        os.makedirs(self.backup_dir, exist_ok=True)

    def _backup(self) -> str:
        """创建配置文件的备份"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(self.backup_dir, f'devices_{timestamp}.py')
        shutil.copy2(self.config_file, backup_file)
        return backup_file

    def _generate_devices_content(self, devices: Dict[str, Any]) -> str:
        """根据设备字典生成 Python 配置文件内容"""
        lines = [
            "# 防火墙设备配置 - 统一配置格式",
            "# 所有设备信息统一维护在此文件",
            "#",
            f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "firewall_devices = {",
        ]

        for name, config in devices.items():
            lines.append(f"    '{name}': {{")
            lines.append(f"        'name': '{config.get('name', name)}',")
            lines.append(f"        'vendor': '{config.get('vendor', 'huawei')}',")
            lines.append(f"        'ip': '{config.get('ip', '')}',")
            lines.append(f"        'port': {config.get('port', 22)},")
            lines.append(f"        'username': '{config.get('username', '')}',")
            lines.append(f"        'password': '{config.get('password', '')}',")
            lines.append(f"        'location': '{config.get('location', '')}',")
            lines.append(f"        'description': '{config.get('description', '')}',")

            zones = config.get('zones', {})
            if zones:
                lines.append("        'zones': {")
                for zone_type, zone_data in zones.items():
                    lines.append(f"            '{zone_type}': {{")
                    if isinstance(zone_data, dict):
                        for zone_name, zone_value in zone_data.items():
                            if isinstance(zone_value, list):
                                lines.append(f"                '{zone_name}': {zone_value},")
                            elif isinstance(zone_value, dict):
                                lines.append(f"                '{zone_name}': {{")
                                if 'net' in zone_value:
                                    lines.append(f"                    'net': {zone_value['net']},")
                                if 'dev' in zone_value:
                                    lines.append(f"                    'dev': {zone_value['dev']},")
                                if 'allow' in zone_value:
                                    lines.append(f"                    'allow': {zone_value['allow']},")
                                lines.append("                },")
                            else:
                                lines.append(f"                '{zone_name}': {zone_value},")
                    lines.append("            },")
                lines.append("        },")
            else:
                lines.append("        'zones': {},")

            lines.append("    },")

        lines.append("}")

        return "\n".join(lines)

    def get_devices(self) -> Dict[str, Any]:
        """获取所有设备配置"""
        from config.devices import firewall_devices
        result = {}
        for name, config in firewall_devices.items():
            result[name] = self._format_device_config(name, config)
        return result

    def _format_device_config(self, name: str, config: Any) -> Dict[str, Any]:
        """格式化设备配置"""
        if not isinstance(config, dict):
            return {'name': name, 'vendor': 'unknown', 'ip': '', 'port': 22, 'username': '', 'password': '', 'location': '', 'description': '', 'zones': {}}

        return {
            'name': config.get('name', name),
            'vendor': config.get('vendor', 'huawei'),
            'ip': config.get('ip', ''),
            'port': config.get('port', 22),
            'username': config.get('username', ''),
            'password': config.get('password', ''),
            'location': config.get('location', ''),
            'description': config.get('description', ''),
            'zones': config.get('zones', {})
        }

    def get_device(self, name: str) -> Optional[Dict[str, Any]]:
        """获取单个设备配置"""
        from config.devices import firewall_devices
        config = firewall_devices.get(name)
        if config:
            return self._format_device_config(name, config)
        return None

    def save_devices(self, devices: Dict[str, Any]) -> Dict[str, Any]:
        """保存所有设备配置（完整重写）"""
        try:
            self._backup()
            content = self._generate_devices_content(devices)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                'status': 'success',
                'message': f'配置已保存，共 {len(devices)} 个设备'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'保存失败: {str(e)}'
            }

    def update_device(self, name: str, device_config: Dict[str, Any]) -> Dict[str, Any]:
        """更新单个设备配置"""
        try:
            from config.devices import firewall_devices

            if name not in firewall_devices:
                return {
                    'status': 'failed',
                    'message': f'设备 {name} 不存在'
                }

            self._backup()

            firewall_devices[name] = device_config
            content = self._generate_devices_content(firewall_devices)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                'status': 'success',
                'message': f'设备 {name} 已更新'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'更新失败: {str(e)}'
            }

    def add_device(self, name: str, device_config: Dict[str, Any]) -> Dict[str, Any]:
        """新增设备"""
        try:
            from config.devices import firewall_devices

            if name in firewall_devices:
                return {
                    'status': 'failed',
                    'message': f'设备 {name} 已存在'
                }

            self._backup()

            firewall_devices[name] = device_config
            content = self._generate_devices_content(firewall_devices)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                'status': 'success',
                'message': f'设备 {name} 已添加'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'添加失败: {str(e)}'
            }

    def delete_device(self, name: str) -> Dict[str, Any]:
        """删除设备"""
        try:
            from config.devices import firewall_devices

            if name not in firewall_devices:
                return {
                    'status': 'failed',
                    'message': f'设备 {name} 不存在'
                }

            self._backup()

            del firewall_devices[name]
            content = self._generate_devices_content(firewall_devices)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                'status': 'success',
                'message': f'设备 {name} 已删除'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'删除失败: {str(e)}'
            }

    def create_backup(self) -> Dict[str, Any]:
        """手动创建备份"""
        try:
            backup_file = self._backup()
            return {
                'status': 'success',
                'message': f'备份已创建',
                'backup_file': backup_file
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'备份失败: {str(e)}'
            }

    def validate_device_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证设备配置格式"""
        errors = []

        required_fields = ['vendor', 'ip']
        for field in required_fields:
            if field not in config or not config[field]:
                errors.append(f'缺少必填字段: {field}')

        if config.get('vendor') not in ['huawei', 'hillstone', 'h3c', 'juniper']:
            errors.append('vendor 必须是: huawei, hillstone, h3c, juniper')

        if config.get('port') and not isinstance(config.get('port'), int):
            errors.append('port 必须是整数')

        zones = config.get('zones', {})
        valid_zone_types = ['edge', 'forward-in', 'forward-out', 'mixed']
        for zone_type in zones.keys():
            if zone_type not in valid_zone_types:
                errors.append(f'zone type 必须是: {", ".join(valid_zone_types)}')

        if errors:
            return {
                'valid': False,
                'errors': errors
            }
        return {'valid': True}


config_manager = ConfigManager()
