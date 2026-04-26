from typing import Dict, List, Any
from datetime import datetime
from database import Database, SecurityPolicy, PolicyAuditLog, FirewallDevice, AddressGroup, PortGroup
from services.path_engine import PathCalculator
from factory import FirewallFactory


class PolicyManager:
    """策略管理器"""

    def __init__(self, db: Database):
        self.db = db
        self.path_calculator = PathCalculator()
        self.factory = FirewallFactory()

    def _get_address_groups_from_db(self) -> Dict[str, List[str]]:
        """从数据库获取所有地址组"""
        session = self.db.get_session()
        try:
            groups = session.query(AddressGroup).all()
            return {g.name: g.addresses or [] for g in groups}
        finally:
            session.close()

    def _get_port_groups_from_db(self) -> Dict[str, Dict]:
        """从数据库获取所有端口组"""
        session = self.db.get_session()
        try:
            groups = session.query(PortGroup).all()
            return {g.name: {"ports": g.ports or [], "protocol": g.protocol} for g in groups}
        finally:
            session.close()

    def generate_policy(self, policy_config: Dict[str, Any]) -> Dict[str, Any]:
        """生成策略配置脚本

        Args:
            policy_config: 策略配置，支持：
                - 单个IP: source_ip, dest_ip, protocol, dest_port
                - 地址组: source_group, dest_group, protocol, port_group

        Returns:
            生成的策略配置和脚本
        """
        source_group = policy_config.get("source_group")
        dest_group = policy_config.get("dest_group")
        port_group = policy_config.get("port_group")

        if source_group or dest_group:
            address_groups = self._get_address_groups_from_db()
            port_groups = self._get_port_groups_from_db()
            return self.generate_policy_with_groups(policy_config, address_groups, port_groups)

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

    def apply_policy(self, policy_config: Dict[str, Any], simulate: bool = False) -> Dict[str, Any]:
        """应用策略到防火墙
        
        Args:
            policy_config: 策略配置
            simulate: 是否为模拟模式（无真实设备时直接保存为已应用）
        """
        device_name = policy_config["device_name"]
        policy_script = policy_config["policy_script"]
        policy_name = policy_config.get("policy_name", "unknown")

        session = self.db.get_session()
        try:
            # 1. 先保存策略到数据库，状态为 applying（下发中）
            policy = SecurityPolicy(
                policy_name=policy_name,
                source_ip=policy_config.get("source_ip", "any"),
                dest_ip=policy_config.get("dest_ip", "any"),
                protocol=policy_config.get("protocol", "tcp"),
                dest_port=policy_config.get("dest_port", "any"),
                action=policy_config.get("action", "permit"),
                source_zone=policy_config.get("source_zone"),
                dest_zone=policy_config.get("dest_zone"),
                device_name=device_name,
                policy_script=policy_script,
                status="applying"
            )
            session.add(policy)
            session.commit()

            # 2. 模拟模式：直接标记为已应用，不连接真实设备
            if simulate:
                policy.status = "applied"
                session.commit()
                
                log = PolicyAuditLog(
                    policy_id=policy.id,
                    action="apply_policy_simulate",
                    operator="system",
                    result="success",
                    details=f"模拟模式：策略已保存到数据库（设备 {device_name}）"
                )
                session.add(log)
                session.commit()
                
                return {
                    "status": "success",
                    "policy_id": policy.id,
                    "device_name": device_name,
                    "message": "策略已保存到数据库（模拟模式，未连接真实设备）"
                }

            # 3. 真实模式：连接防火墙设备并下发配置
            device = self._get_device_by_name(device_name)
            if not device:
                policy.status = "failed"
                policy.error_message = f"设备 {device_name} 不存在"
                session.commit()
                return {
                    "status": "failed",
                    "policy_id": policy.id,
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

            # 4. 根据应用结果更新策略状态
            if result.get("status") == "success":
                policy.status = "applied"
                policy.error_message = None
            else:
                policy.status = "failed"
                policy.error_message = result.get("message", "应用失败")
            session.commit()

            # 5. 记录审计日志
            log = PolicyAuditLog(
                policy_id=policy.id,
                action="apply_policy",
                operator="system",
                result=result.get("status"),
                details=f"应用到设备 {device_name}: {result.get('message')}"
            )
            session.add(log)
            session.commit()

            return {
                "status": result.get("status"),
                "policy_id": policy.id,
                "device_name": device_name,
                "message": result.get("message")
            }
            
        except Exception as e:
            session.rollback()
            # 如果策略已创建，标记为失败
            if 'policy' in locals() and policy.id:
                policy.status = "failed"
                policy.error_message = str(e)
                session.commit()
            
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

    def generate_policy_with_groups(self, policy_config: Dict[str, Any], address_groups: Dict[str, Any], port_groups: Dict[str, Any]) -> Dict[str, Any]:
        """基于地址组和端口组生成策略配置

        Args:
            policy_config: 策略配置，包含 policy_name, source_group, dest_group, port_group, protocol
            address_groups: 地址组字典，{group_name: [ips]}
            port_groups: 端口组字典，{group_name: [ports]}

        Returns:
            生成的策略配置，包含合并后的路径组
        """
        source_group = policy_config.get("source_group")
        dest_group = policy_config.get("dest_group")
        port_group = policy_config.get("port_group")
        protocol = policy_config.get("protocol", "tcp")
        policy_name = policy_config.get("policy_name")

        source_ips = address_groups.get(source_group, []) if source_group else []
        dest_ips = address_groups.get(dest_group, []) if dest_group else []
        port_group_data = port_groups.get(port_group, {}) if port_group else {}
        ports = port_group_data.get("ports", []) if port_group_data else []
        port_group_protocol = port_group_data.get("protocol", "tcp") if port_group_data else "tcp"

        if not source_ips or not dest_ips:
            return {
                "status": "error",
                "message": "源地址组或目的地址组不能为空"
            }

        source_ips = self.path_calculator.expand_ip_ranges(source_ips)
        dest_ips = self.path_calculator.expand_ip_ranges(dest_ips)

        effective_protocol = port_group_protocol if port_group else protocol

        ip_pairs = [(src, dst) for src in source_ips for dst in dest_ips]

        paths = self.path_calculator.calculate_paths_for_ip_pairs(ip_pairs)

        merged_path_groups = self.path_calculator.merge_paths_by_consistency(
            paths, source_ips, dest_ips, ip_pairs
        )

        all_firewall_policies = []
        for path_group in merged_path_groups:
            for fw_policy in path_group.get("firewall_policies", []):
                device_config = {
                    "name": fw_policy["device_name"],
                    "vendor": self._get_device_vendor(fw_policy["device_name"]),
                    "ip": self._get_device_ip(fw_policy["device_name"]),
                    "port": self._get_device_port(fw_policy["device_name"]),
                    "zone_mappings": {}
                }

                fw_policy["protocol"] = effective_protocol
                fw_policy["source_ip"] = source_group if source_group else ",".join(fw_policy.get("source_ips", []))
                fw_policy["dest_ip"] = dest_group if dest_group else ",".join(fw_policy.get("dest_ips", []))
                fw_policy["dest_port"] = port_group if port_group else ("any" if not ports else (",".join(ports) if len(ports) > 1 else ports[0]))
                fw_policy["generation_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                adapter = self.factory.create_firewall(device_config)
                policy_script = adapter.generate_cli_command(fw_policy)

                fw_policy["policy_script"] = policy_script

                merge_key = (
                    fw_policy["device_name"],
                    fw_policy.get("source_zone", ""),
                    fw_policy.get("dest_zone", ""),
                    source_group if source_group else ",".join(sorted(fw_policy.get("source_ips", []))),
                    dest_group if dest_group else ",".join(sorted(fw_policy.get("dest_ips", []))),
                    effective_protocol,
                    fw_policy["dest_port"]
                )

                existing_idx = None
                for idx, p in enumerate(all_firewall_policies):
                    existing_merge_key = (
                        p["device_name"],
                        p.get("source_zone", ""),
                        p.get("dest_zone", ""),
                        p.get("source_ip", ""),
                        p.get("dest_ip", ""),
                        p.get("protocol", ""),
                        p.get("dest_port", "")
                    )
                    if existing_merge_key == merge_key:
                        existing_idx = idx
                        break

                if existing_idx is not None:
                    existing_policy = all_firewall_policies[existing_idx]
                    existing_policy["source_ips"] = list(set(existing_policy.get("source_ips", []) + fw_policy.get("source_ips", [])))
                    existing_policy["dest_ips"] = list(set(existing_policy.get("dest_ips", []) + fw_policy.get("dest_ips", [])))
                    existing_policy["source_dest_pairs"] = list(set([tuple(x) for x in existing_policy.get("source_dest_pairs", [])] + [tuple(x) for x in fw_policy.get("source_dest_pairs", [])]))

                    if existing_policy.get("source_ip") == source_group and existing_policy.get("source_zone") == fw_policy.get("source_zone") and existing_policy.get("dest_zone") == fw_policy.get("dest_zone"):
                        merged_fw_policy = existing_policy.copy()
                        merged_fw_policy["source_ips"] = existing_policy["source_ips"]
                        merged_fw_policy["dest_ips"] = existing_policy["dest_ips"]
                        merged_fw_policy["source_dest_pairs"] = existing_policy["source_dest_pairs"]
                        existing_policy["policy_script"] = adapter.generate_cli_command(merged_fw_policy)
                else:
                    all_firewall_policies.append(fw_policy)

        path_group_results = []
        for path_group in merged_path_groups:
            path_device_names = [fw["device_name"] for fw in path_group["path"]]
            unique_path_devices = []
            seen = set()
            for dn in path_device_names:
                if dn not in seen:
                    unique_path_devices.append(dn)
                    seen.add(dn)

            path_policies = []
            for dn in unique_path_devices:
                for p in all_firewall_policies:
                    if p["device_name"] == dn and p.get("source_zone") == path_group["path"][unique_path_devices.index(dn)].get("source_zone") and p.get("dest_zone") == path_group["path"][unique_path_devices.index(dn)].get("dest_zone"):
                        path_policies.append(p)
                        break

            path_group_results.append({
                "path_description": path_group["path_description"],
                "source_ips": path_group["source_ips"],
                "dest_ips": path_group["dest_ips"],
                "firewall_count": path_group["firewall_count"],
                "policies": path_policies
            })

        unique_firewalls = list(set(fw["device_name"] for fw in all_firewall_policies))

        if len(merged_path_groups) == 1:
            path_summary = f"所有IP对({len(source_ips)}个源 x {len(dest_ips)}个目的)路径一致，共经过 {len(unique_firewalls)} 台防火墙"
        else:
            path_summary = f"IP对路径不一致，分为 {len(merged_path_groups)} 组，共经过 {len(unique_firewalls)} 台防火墙"

        return {
            "status": "generated",
            "policy_name": policy_name,
            "source_group": source_group,
            "dest_group": dest_group,
            "port_group": port_group,
            "protocol": effective_protocol,
            "source_ips": source_ips,
            "dest_ips": dest_ips,
            "total_ip_pairs": len(ip_pairs),
            "path_summary": path_summary,
            "firewall_count": len(unique_firewalls),
            "firewall_policies": all_firewall_policies,
            "merged_path_groups": len(merged_path_groups),
            "path_group_details": path_group_results,
            "generated_at": datetime.now().isoformat()
        }

    def detect_policy_conflicts(self, new_policy: Dict[str, Any], existing_policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检测策略冲突

        Args:
            new_policy: 新策略配置
            existing_policies: 现有策略列表

        Returns:
            冲突列表
        """
        conflicts = []

        for existing in existing_policies:
            if self._is_conflicting(new_policy, existing):
                conflicts.append({
                    "existing_policy_id": existing.get("id"),
                    "existing_policy_name": existing.get("policy_name"),
                    "reason": "相同源/目的/端口/协议的策略已存在"
                })

        return conflicts

    def _is_conflicting(self, policy1: Dict[str, Any], policy2: Dict[str, Any]) -> bool:
        """检查两个策略是否冲突"""
        p1_source = set(policy1.get("source_ips", []))
        p2_source = set(policy2.get("source_ips", []))
        p1_dest = set(policy1.get("dest_ips", []))
        p2_dest = set(policy2.get("dest_ips", []))

        if p1_source & p2_source and p1_dest & p2_dest:
            if policy1.get("dest_port") == policy2.get("dest_port"):
                if policy1.get("protocol") == policy2.get("protocol"):
                    return True

        return False
