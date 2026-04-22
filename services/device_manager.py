from typing import Dict, List, Any
from datetime import datetime
from factory import FirewallFactory
from database import Database, FirewallDevice
from config.devices import DEVICES


class DeviceManager:
    """防火墙设备管理器"""

    def __init__(self, db: Database):
        self.db = db
        self.factory = FirewallFactory()

    def register_device(self, device_config: Dict[str, Any]) -> Dict[str, Any]:
        """注册防火墙设备"""
        session = self.db.get_session()
        try:
            existing = session.query(FirewallDevice).filter(
                FirewallDevice.name == device_config["name"]
            ).first()

            if existing:
                existing.vendor = device_config.get("vendor", existing.vendor)
                existing.ip = device_config.get("ip", existing.ip)
                existing.port = device_config.get("port", existing.port)
                existing.username = device_config.get("username", existing.username)
                existing.password = device_config.get("password", existing.password)
                existing.location = device_config.get("location", existing.location)
                existing.zone_mappings = device_config.get("zone_mappings", existing.zone_mappings)
                existing.connected_networks = device_config.get("connected_networks", existing.connected_networks)
                existing.routing_table = device_config.get("routing_table", existing.routing_table)
                existing.updated_at = datetime.now()
                session.commit()
                return {
                    "status": "updated",
                    "message": f"设备 {device_config['name']} 已更新",
                    "device": existing.to_dict()
                }

            device = FirewallDevice(
                name=device_config["name"],
                vendor=device_config["vendor"],
                ip=device_config["ip"],
                port=device_config.get("port", 22),
                username=device_config.get("username"),
                password=device_config.get("password"),
                location=device_config.get("location", "Unknown"),
                zone_mappings=device_config.get("zone_mappings", {}),
                connected_networks=device_config.get("connected_networks", []),
                routing_table=device_config.get("routing_table", []),
                status="offline"
            )
            session.add(device)
            session.commit()
            return {
                "status": "registered",
                "message": f"设备 {device_config['name']} 注册成功",
                "device": device.to_dict()
            }
        except Exception as e:
            session.rollback()
            return {
                "status": "failed",
                "message": f"注册失败: {str(e)}"
            }
        finally:
            session.close()

    def check_heartbeat(self, device_name: str) -> Dict[str, Any]:
        """检查设备心跳"""
        session = self.db.get_session()
        try:
            device = session.query(FirewallDevice).filter(
                FirewallDevice.name == device_name
            ).first()

            if not device:
                return {
                    "status": "failed",
                    "message": f"设备 {device_name} 不存在"
                }

            device_config = {
                "name": device.name,
                "vendor": device.vendor,
                "ip": device.ip,
                "port": device.port,
                "username": device.username,
                "password": device.password,
                "location": device.location,
                "zone_mappings": device.zone_mappings
            }

            adapter = self.factory.create_firewall(device_config)
            heartbeat_result = adapter.check_heartbeat()

            device.status = heartbeat_result.get("status", "unknown")
            device.last_heartbeat = datetime.now()
            session.commit()

            return heartbeat_result
        except Exception as e:
            return {
                "status": "error",
                "device_name": device_name,
                "message": str(e)
            }
        finally:
            session.close()

    def get_all_devices(self) -> List[Dict[str, Any]]:
        """获取所有设备"""
        session = self.db.get_session()
        try:
            devices = session.query(FirewallDevice).all()
            return [device.to_dict() for device in devices]
        finally:
            session.close()

    def get_device(self, device_name: str) -> Dict[str, Any]:
        """获取单个设备信息"""
        session = self.db.get_session()
        try:
            device = session.query(FirewallDevice).filter(
                FirewallDevice.name == device_name
            ).first()

            if device:
                return device.to_dict()
            return None
        finally:
            session.close()

    def delete_device(self, device_name: str) -> Dict[str, Any]:
        """删除设备"""
        session = self.db.get_session()
        try:
            device = session.query(FirewallDevice).filter(
                FirewallDevice.name == device_name
            ).first()

            if device:
                session.delete(device)
                session.commit()
                return {
                    "status": "success",
                    "message": f"设备 {device_name} 已删除"
                }
            return {
                "status": "failed",
                "message": f"设备 {device_name} 不存在"
            }
        except Exception as e:
            session.rollback()
            return {
                "status": "failed",
                "message": str(e)
            }
        finally:
            session.close()

    def batch_register_from_config(self) -> List[Dict[str, Any]]:
        """从配置文件批量注册设备"""
        results = []
        for device_name, device_config in DEVICES.items():
            device_config["name"] = device_name
            result = self.register_device(device_config)
            results.append(result)
        return results
