from typing import Dict, List, Any
from datetime import datetime
from database import Database, SecurityPolicy, PolicyAuditLog, FirewallDevice
from services.path_engine import PathCalculator
from factory import FirewallFactory


class PolicyManager:
    """策略管理器"""

    def __init__(self, db: Database):
        self.db = db
        self.path_calculator = PathCalculator()
        self.factory = FirewallFactory()

    def generate_policy(self, policy_config: Dict[str, Any]) -> Dict[str, Any]:
        """生成策略配置脚本

        Args:
            policy_config: 策略配置，包含 source_ip, dest_ip, protocol, dest_port, policy_name

        Returns:
            生成的策略配置和脚本
        """
        source_ip = policy_config["source_ip"]
        dest_ip = policy_config["dest_ip"]
        protocol = policy_config["protocol"]
        dest_port = policy_config["dest_port"]
        policy_name = policy_config["policy_name"]

        full_config = self.path_calculator.get_policy_config(
            source_ip, dest_ip, protocol, dest_port, policy_name
        )

        firewall_policies = []
        for fw_policy in full_config["firewall_policies"]:
            device_config = {
                "name": fw_policy["device_name"],
                "vendor": self._get_device_vendor(fw_policy["device_name"]),
                "ip": self._get_device_ip(fw_policy["device_name"]),
                "port": self._get_device_port(fw_policy["device_name"]),
                "zone_mappings": {}
            }

            adapter = self.factory.create_firewall(device_config)
            policy_script = adapter.generate_cli_command(fw_policy)

            firewall_policies.append({
                "device_name": fw_policy["device_name"],
                "vendor": fw_policy["vendor"],
                "source_zone": fw_policy["source_zone"],
                "dest_zone": fw_policy["dest_zone"],
                "source_zone_description": fw_policy.get("source_zone_description", ""),
                "dest_zone_description": fw_policy.get("dest_zone_description", ""),
                "flow_direction": fw_policy.get("flow_direction", ""),
                "sequence": fw_policy.get("sequence", 0),
                "policy_script": policy_script
            })

        full_config["firewall_policies"] = firewall_policies
        full_config["status"] = "generated"
        full_config["generated_at"] = datetime.now().isoformat()

        return full_config

    def save_policy(self, policy_config: Dict[str, Any]) -> Dict[str, Any]:
        """保存策略到数据库"""
        session = self.db.get_session()
        try:
            policy = SecurityPolicy(
                policy_name=policy_config["policy_name"],
                source_ip=policy_config["source_ip"],
                dest_ip=policy_config["dest_ip"],
                protocol=policy_config["protocol"],
                dest_port=policy_config["dest_port"],
                source_zone=policy_config.get("source_zone"),
                dest_zone=policy_config.get("dest_zone"),
                device_name=policy_config.get("device_name"),
                policy_script=policy_config.get("policy_script"),
                status="pending"
            )
            session.add(policy)
            session.commit()
            return {
                "status": "saved",
                "policy_id": policy.id,
                "message": "策略保存成功"
            }
        except Exception as e:
            session.rollback()
            return {
                "status": "failed",
                "message": str(e)
            }
        finally:
            session.close()

    def apply_policy(self, policy_config: Dict[str, Any]) -> Dict[str, Any]:
        """应用策略到防火墙"""
        device_name = policy_config["device_name"]
        policy_script = policy_config["policy_script"]

        session = self.db.get_session()
        try:
            device = self._get_device_by_name(device_name)
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
            result = adapter.apply_policy(policy_script)

            log = PolicyAuditLog(
                policy_id=policy_config.get("policy_id"),
                action="apply_policy",
                operator="system",
                result=result.get("status"),
                details=f"应用到设备 {device_name}: {result.get('message')}"
            )
            session.add(log)
            session.commit()

            if result.get("status") == "success":
                policy = session.query(SecurityPolicy).filter(
                    SecurityPolicy.policy_name == policy_config["policy_name"]
                ).first()
                if policy:
                    policy.status = "applied"
                    session.commit()

            return result
        except Exception as e:
            return {
                "status": "failed",
                "message": str(e)
            }
        finally:
            session.close()

    def get_all_policies(self) -> List[Dict[str, Any]]:
        """获取所有策略"""
        session = self.db.get_session()
        try:
            policies = session.query(SecurityPolicy).all()
            return [policy.to_dict() for policy in policies]
        finally:
            session.close()

    def get_policy(self, policy_id: int) -> Dict[str, Any]:
        """获取单个策略"""
        session = self.db.get_session()
        try:
            policy = session.query(SecurityPolicy).filter(
                SecurityPolicy.id == policy_id
            ).first()
            if policy:
                return policy.to_dict()
            return None
        finally:
            session.close()

    def _get_device_by_name(self, device_name: str) -> Any:
        """根据名称获取设备"""
        session = self.db.get_session()
        try:
            device = session.query(FirewallDevice).filter(
                FirewallDevice.name == device_name
            ).first()
            return device
        finally:
            session.close()

    def _get_device_vendor(self, device_name: str) -> str:
        """获取设备厂商"""
        device = self._get_device_by_name(device_name)
        if device:
            return device.vendor
        from config.devices import DEVICES
        return DEVICES.get(device_name, {}).get("vendor", "huawei")

    def _get_device_ip(self, device_name: str) -> str:
        """获取设备IP"""
        device = self._get_device_by_name(device_name)
        if device:
            return device.ip
        from config.devices import DEVICES
        return DEVICES.get(device_name, {}).get("ip", "192.168.1.10")

    def _get_device_port(self, device_name: str) -> int:
        """获取设备端口"""
        device = self._get_device_by_name(device_name)
        if device:
            return device.port
        from config.devices import DEVICES
        return DEVICES.get(device_name, {}).get("port", 22)
