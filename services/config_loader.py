from database import Database, FirewallDevice


class ConfigLoader:
    """配置加载器 - 直接从数据库读取设备配置"""

    def __init__(self):
        self.db = Database()

    def get_devices(self):
        """获取所有设备配置"""
        session = self.db.get_session()
        try:
            devices = session.query(FirewallDevice).all()
            result = {}
            for device in devices:
                result[device.name] = {
                    "name": device.name,
                    "vendor": device.vendor,
                    "ip": device.ip,
                    "port": device.port,
                    "username": device.username,
                    "password": device.password,
                    "location": device.location,
                    "zone_mappings": device.zone_mappings or {},
                    "connected_networks": device.connected_networks or [],
                    "routing_table": device.routing_table or []
                }
            return result
        finally:
            session.close()

    def get_device(self, name):
        """获取单个设备配置"""
        session = self.db.get_session()
        try:
            device = session.query(FirewallDevice).filter(
                FirewallDevice.name == name
            ).first()
            if not device:
                return None
            return {
                "name": device.name,
                "vendor": device.vendor,
                "ip": device.ip,
                "port": device.port,
                "username": device.username,
                "password": device.password,
                "location": device.location,
                "zone_mappings": device.zone_mappings or {},
                "connected_networks": device.connected_networks or [],
                "routing_table": device.routing_table or []
            }
        finally:
            session.close()


config_loader = ConfigLoader()
