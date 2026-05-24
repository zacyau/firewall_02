# 配置管理器 - 基于数据库的设备配置管理
# config/devices.py 仅作为初始化种子，运行时数据源为数据库

from typing import Dict, Any, Optional
from database import Database, FirewallDevice


class ConfigManager:
    """设备配置管理器 - 数据库驱动"""

    def __init__(self, db: Database = None):
        self.db = db or Database()

    def get_devices(self) -> Dict[str, Any]:
        """获取所有设备配置，返回 {name: config} 格式"""
        session = self.db.get_session()
        try:
            devices = session.query(FirewallDevice).all()
            result = {}
            for d in devices:
                result[d.name] = self._device_to_config(d)
            return result
        finally:
            session.close()

    def get_device(self, name: str) -> Optional[Dict[str, Any]]:
        """获取单个设备配置"""
        session = self.db.get_session()
        try:
            device = session.query(FirewallDevice).filter(FirewallDevice.name == name).first()
            if device:
                return self._device_to_config(device)
            return None
        finally:
            session.close()

    def save_devices(self, devices: Dict[str, Any]) -> Dict[str, Any]:
        """保存所有设备配置（全量覆盖）"""
        session = self.db.get_session()
        try:
            # 清空旧数据
            session.query(FirewallDevice).delete()

            for name, config in devices.items():
                device = self._config_to_device(name, config)
                session.add(device)

            session.commit()
            return {
                'status': 'success',
                'message': f'配置已保存，共 {len(devices)} 个设备'
            }
        except Exception as e:
            session.rollback()
            return {
                'status': 'failed',
                'message': f'保存失败: {str(e)}'
            }
        finally:
            session.close()

    def update_device(self, name: str, device_config: Dict[str, Any]) -> Dict[str, Any]:
        """更新单个设备配置"""
        session = self.db.get_session()
        try:
            device = session.query(FirewallDevice).filter(FirewallDevice.name == name).first()
            if not device:
                return {
                    'status': 'failed',
                    'message': f'设备 {name} 不存在'
                }

            self._apply_config_to_device(device, device_config)
            session.commit()
            return {
                'status': 'success',
                'message': f'设备 {name} 已更新'
            }
        except Exception as e:
            session.rollback()
            return {
                'status': 'failed',
                'message': f'更新失败: {str(e)}'
            }
        finally:
            session.close()

    def add_device(self, name: str, device_config: Dict[str, Any]) -> Dict[str, Any]:
        """新增设备"""
        session = self.db.get_session()
        try:
            existing = session.query(FirewallDevice).filter(FirewallDevice.name == name).first()
            if existing:
                return {
                    'status': 'failed',
                    'message': f'设备 {name} 已存在'
                }

            device = self._config_to_device(name, device_config)
            session.add(device)
            session.commit()
            return {
                'status': 'success',
                'message': f'设备 {name} 已添加'
            }
        except Exception as e:
            session.rollback()
            return {
                'status': 'failed',
                'message': f'添加失败: {str(e)}'
            }
        finally:
            session.close()

    def delete_device(self, name: str) -> Dict[str, Any]:
        """删除设备"""
        session = self.db.get_session()
        try:
            device = session.query(FirewallDevice).filter(FirewallDevice.name == name).first()
            if not device:
                return {
                    'status': 'failed',
                    'message': f'设备 {name} 不存在'
                }

            session.delete(device)
            session.commit()
            return {
                'status': 'success',
                'message': f'设备 {name} 已删除'
            }
        except Exception as e:
            session.rollback()
            return {
                'status': 'failed',
                'message': f'删除失败: {str(e)}'
            }
        finally:
            session.close()

    def seed_from_config(self) -> Dict[str, Any]:
        """从配置文件种子导入数据库（仅数据库为空时执行）"""
        session = self.db.get_session()
        try:
            count = session.query(FirewallDevice).count()
            if count > 0:
                return {
                    'status': 'skipped',
                    'message': f'数据库已有 {count} 个设备，跳过种子导入'
                }

            from config.devices import firewall_devices
            for name, config in firewall_devices.items():
                device = self._config_to_device(name, config)
                session.add(device)

            session.commit()
            return {
                'status': 'success',
                'message': f'已从配置文件导入 {len(firewall_devices)} 个设备'
            }
        except Exception as e:
            session.rollback()
            return {
                'status': 'failed',
                'message': f'种子导入失败: {str(e)}'
            }
        finally:
            session.close()

    def export_to_dict(self) -> Dict[str, Any]:
        """导出所有设备配置为字典格式（用于备份/下载）"""
        return self.get_devices()

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

    # ---- 内部方法 ----

    def _device_to_config(self, device: FirewallDevice) -> Dict[str, Any]:
        """ORM 对象转配置字典"""
        return {
            'name': device.name,
            'vendor': device.vendor,
            'ip': device.ip,
            'port': device.port or 22,
            'username': device.username or '',
            'password': device.password or '',
            'location': device.location or '',
            'description': device.description or '',
            'zones': device.zones or {},
        }

    def _config_to_device(self, name: str, config: Dict[str, Any]) -> FirewallDevice:
        """配置字典转 ORM 对象"""
        return FirewallDevice(
            name=name,
            vendor=config.get('vendor', 'huawei'),
            ip=config.get('ip', ''),
            port=config.get('port', 22),
            username=config.get('username', ''),
            password=config.get('password', ''),
            location=config.get('location', ''),
            description=config.get('description', ''),
            zones=config.get('zones', {}),
        )

    def _apply_config_to_device(self, device: FirewallDevice, config: Dict[str, Any]):
        """将配置字典应用到已有 ORM 对象"""
        device.vendor = config.get('vendor', device.vendor)
        device.ip = config.get('ip', device.ip)
        device.port = config.get('port', device.port)
        device.username = config.get('username', device.username)
        device.password = config.get('password', device.password)
        device.location = config.get('location', device.location)
        device.description = config.get('description', device.description)
        device.zones = config.get('zones', device.zones)


# 延迟初始化单例，避免循环导入
_config_manager = None

def get_config_manager() -> ConfigManager:
    """获取 ConfigManager 单例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
