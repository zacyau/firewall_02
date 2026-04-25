from typing import Dict, List, Any, Optional
from datetime import datetime
from database import Database, AddressGroup, PortGroup, AddressGroupDeviceStatus, PortGroupDeviceStatus, FirewallDevice
from factory.firewall_factory import FirewallFactory


class GroupManager:
    """组管理器 - 管理地址组和端口组"""

    def __init__(self, db: Database):
        self.db = db
        self.factory = FirewallFactory()

    def create_address_group(self, name: str, addresses: List[str], description: str = None) -> Dict[str, Any]:
        """创建地址组"""
        session = self.db.get_session()
        try:
            existing = session.query(AddressGroup).filter(AddressGroup.name == name).first()
            if existing:
                return {"status": "error", "message": f"地址组 {name} 已存在"}

            address_group = AddressGroup(
                name=name,
                description=description,
                addresses=addresses
            )
            session.add(address_group)
            session.commit()
            return {"status": "success", "message": "地址组创建成功", "data": address_group.to_dict()}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def get_address_group(self, name: str) -> Optional[Dict[str, Any]]:
        """获取地址组"""
        session = self.db.get_session()
        try:
            group = session.query(AddressGroup).filter(AddressGroup.name == name).first()
            return group.to_dict() if group else None
        finally:
            session.close()

    def get_all_address_groups(self) -> List[Dict[str, Any]]:
        """获取所有地址组"""
        session = self.db.get_session()
        try:
            groups = session.query(AddressGroup).all()
            return [g.to_dict() for g in groups]
        finally:
            session.close()

    def update_address_group(self, name: str, addresses: List[str] = None, description: str = None) -> Dict[str, Any]:
        """更新地址组"""
        session = self.db.get_session()
        try:
            group = session.query(AddressGroup).filter(AddressGroup.name == name).first()
            if not group:
                return {"status": "error", "message": f"地址组 {name} 不存在"}

            if addresses is not None:
                group.addresses = addresses
            if description is not None:
                group.description = description

            session.commit()
            return {"status": "success", "message": "地址组更新成功", "data": group.to_dict()}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def delete_address_group(self, name: str) -> Dict[str, Any]:
        """删除地址组"""
        session = self.db.get_session()
        try:
            group = session.query(AddressGroup).filter(AddressGroup.name == name).first()
            if not group:
                return {"status": "error", "message": f"地址组 {name} 不存在"}

            session.delete(group)
            session.commit()
            return {"status": "success", "message": "地址组删除成功"}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def create_port_group(self, name: str, ports: List[str], protocol: str = 'tcp', description: str = None) -> Dict[str, Any]:
        """创建端口组"""
        session = self.db.get_session()
        try:
            existing = session.query(PortGroup).filter(PortGroup.name == name).first()
            if existing:
                return {"status": "error", "message": f"端口组 {name} 已存在"}

            port_group = PortGroup(
                name=name,
                description=description,
                ports=ports,
                protocol=protocol
            )
            session.add(port_group)
            session.commit()
            return {"status": "success", "message": "端口组创建成功", "data": port_group.to_dict()}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def get_port_group(self, name: str) -> Optional[Dict[str, Any]]:
        """获取端口组"""
        session = self.db.get_session()
        try:
            group = session.query(PortGroup).filter(PortGroup.name == name).first()
            return group.to_dict() if group else None
        finally:
            session.close()

    def get_all_port_groups(self) -> List[Dict[str, Any]]:
        """获取所有端口组"""
        session = self.db.get_session()
        try:
            groups = session.query(PortGroup).all()
            return [g.to_dict() for g in groups]
        finally:
            session.close()

    def update_port_group(self, name: str, ports: List[str] = None, protocol: str = None, description: str = None) -> Dict[str, Any]:
        """更新端口组"""
        session = self.db.get_session()
        try:
            group = session.query(PortGroup).filter(PortGroup.name == name).first()
            if not group:
                return {"status": "error", "message": f"端口组 {name} 不存在"}

            if ports is not None:
                group.ports = ports
            if protocol is not None:
                group.protocol = protocol
            if description is not None:
                group.description = description

            session.commit()
            return {"status": "success", "message": "端口组更新成功", "data": group.to_dict()}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def delete_port_group(self, name: str) -> Dict[str, Any]:
        """删除端口组"""
        session = self.db.get_session()
        try:
            group = session.query(PortGroup).filter(PortGroup.name == name).first()
            if not group:
                return {"status": "error", "message": f"端口组 {name} 不存在"}

            session.delete(group)
            session.commit()
            return {"status": "success", "message": "端口组删除成功"}
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def get_address_group_device_status(self, group_name: str) -> List[Dict[str, Any]]:
        """获取地址组在各防火墙上的配置状态"""
        session = self.db.get_session()
        try:
            statuses = session.query(AddressGroupDeviceStatus).filter(
                AddressGroupDeviceStatus.group_name == group_name
            ).all()
            return [s.to_dict() for s in statuses]
        finally:
            session.close()

    def get_port_group_device_status(self, group_name: str) -> List[Dict[str, Any]]:
        """获取端口组在各防火墙上的配置状态"""
        session = self.db.get_session()
        try:
            statuses = session.query(PortGroupDeviceStatus).filter(
                PortGroupDeviceStatus.group_name == group_name
            ).all()
            return [s.to_dict() for s in statuses]
        finally:
            session.close()

    def _get_all_devices(self) -> List[FirewallDevice]:
        """获取所有防火墙设备"""
        session = self.db.get_session()
        try:
            return session.query(FirewallDevice).all()
        finally:
            session.close()

    def _generate_address_group_config(self, group: AddressGroup, device: FirewallDevice) -> str:
        """生成地址组配置脚本"""
        device_config = {
            "name": device.name,
            "vendor": device.vendor,
            "ip": device.ip,
            "port": device.port,
            "zone_mappings": device.zone_mappings or {}
        }
        adapter = self.factory.create_firewall(device_config)

        context = {
            "group_name": group.name,
            "addresses": group.addresses or [],
            "description": group.description or "",
            "device_name": device.name,
            "vendor": device.vendor
        }

        return adapter._render_template("address_group.j2", context)

    def _generate_port_group_config(self, group: PortGroup, device: FirewallDevice) -> str:
        """生成端口组配置脚本"""
        device_config = {
            "name": device.name,
            "vendor": device.vendor,
            "ip": device.ip,
            "port": device.port,
            "zone_mappings": device.zone_mappings or {}
        }
        adapter = self.factory.create_firewall(device_config)

        context = {
            "group_name": group.name,
            "ports": group.ports or [],
            "protocol": group.protocol or "tcp",
            "description": group.description or "",
            "device_name": device.name,
            "vendor": device.vendor
        }

        return adapter._render_template("port_group.j2", context)

    def generate_address_group_configs(self, group_name: str) -> Dict[str, Any]:
        """生成地址组在所有防火墙上的配置

        1. 从数据库获取地址组信息
        2. 获取所有防火墙设备
        3. 检查每台防火墙是否已配置该地址组
        4. 对未配置的防火墙生成配置脚本
        """
        session = self.db.get_session()
        try:
            group = session.query(AddressGroup).filter(AddressGroup.name == group_name).first()
            if not group:
                return {"status": "error", "message": f"地址组 {group_name} 不存在"}

            devices = session.query(FirewallDevice).all()
            if not devices:
                return {"status": "error", "message": "没有可用的防火墙设备"}

            results = []
            for device in devices:
                status = session.query(AddressGroupDeviceStatus).filter(
                    AddressGroupDeviceStatus.group_name == group_name,
                    AddressGroupDeviceStatus.device_name == device.name
                ).first()

                if status and status.status == "created":
                    results.append({
                        "device_name": device.name,
                        "vendor": device.vendor,
                        "status": "created",
                        "config_script": status.config_script,
                        "message": "该地址组已在此防火墙上配置"
                    })
                else:
                    config_script = self._generate_address_group_config(group, device)

                    if not status:
                        status = AddressGroupDeviceStatus(
                            group_name=group_name,
                            device_name=device.name,
                            status="pending",
                            config_script=config_script
                        )
                        session.add(status)
                    else:
                        status.config_script = config_script
                        status.status = "pending"

                    results.append({
                        "device_name": device.name,
                        "vendor": device.vendor,
                        "status": "pending",
                        "config_script": config_script,
                        "message": "配置已生成，等待应用"
                    })

            session.commit()
            return {
                "status": "success",
                "group_name": group_name,
                "devices": results
            }
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def generate_port_group_configs(self, group_name: str) -> Dict[str, Any]:
        """生成端口组在所有防火墙上的配置

        1. 从数据库获取端口组信息
        2. 获取所有防火墙设备
        3. 检查每台防火墙是否已配置该端口组
        4. 对未配置的防火墙生成配置脚本
        """
        session = self.db.get_session()
        try:
            group = session.query(PortGroup).filter(PortGroup.name == group_name).first()
            if not group:
                return {"status": "error", "message": f"端口组 {group_name} 不存在"}

            devices = session.query(FirewallDevice).all()
            if not devices:
                return {"status": "error", "message": "没有可用的防火墙设备"}

            results = []
            for device in devices:
                status = session.query(PortGroupDeviceStatus).filter(
                    PortGroupDeviceStatus.group_name == group_name,
                    PortGroupDeviceStatus.device_name == device.name
                ).first()

                if status and status.status == "created":
                    results.append({
                        "device_name": device.name,
                        "vendor": device.vendor,
                        "status": "created",
                        "config_script": status.config_script,
                        "message": "该端口组已在此防火墙上配置"
                    })
                else:
                    config_script = self._generate_port_group_config(group, device)

                    if not status:
                        status = PortGroupDeviceStatus(
                            group_name=group_name,
                            device_name=device.name,
                            status="pending",
                            config_script=config_script
                        )
                        session.add(status)
                    else:
                        status.config_script = config_script
                        status.status = "pending"

                    results.append({
                        "device_name": device.name,
                        "vendor": device.vendor,
                        "status": "pending",
                        "config_script": config_script,
                        "message": "配置已生成，等待应用"
                    })

            session.commit()
            return {
                "status": "success",
                "group_name": group_name,
                "devices": results
            }
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def apply_address_group_config(self, group_name: str, device_name: str) -> Dict[str, Any]:
        """应用地址组配置到指定防火墙

        暂时模拟应用成功，直接更新数据库状态为已创建
        待后期对接真实防火墙CLI后再修改
        """
        session = self.db.get_session()
        try:
            status = session.query(AddressGroupDeviceStatus).filter(
                AddressGroupDeviceStatus.group_name == group_name,
                AddressGroupDeviceStatus.device_name == device_name
            ).first()

            if not status:
                return {"status": "error", "message": f"未找到地址组 {group_name} 在设备 {device_name} 上的配置记录"}

            if status.status == "created":
                return {"status": "success", "message": f"地址组 {group_name} 已在设备 {device_name} 上配置"}

            status.status = "created"
            status.applied_at = datetime.now()
            session.commit()

            return {
                "status": "success",
                "message": f"地址组 {group_name} 已成功应用到设备 {device_name}",
                "device_name": device_name,
                "group_name": group_name,
                "applied_at": status.applied_at.isoformat()
            }
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def apply_port_group_config(self, group_name: str, device_name: str) -> Dict[str, Any]:
        """应用端口组配置到指定防火墙

        暂时模拟应用成功，直接更新数据库状态为已创建
        待后期对接真实防火墙CLI后再修改
        """
        session = self.db.get_session()
        try:
            status = session.query(PortGroupDeviceStatus).filter(
                PortGroupDeviceStatus.group_name == group_name,
                PortGroupDeviceStatus.device_name == device_name
            ).first()

            if not status:
                return {"status": "error", "message": f"未找到端口组 {group_name} 在设备 {device_name} 上的配置记录"}

            if status.status == "created":
                return {"status": "success", "message": f"端口组 {group_name} 已在设备 {device_name} 上配置"}

            status.status = "created"
            status.applied_at = datetime.now()
            session.commit()

            return {
                "status": "success",
                "message": f"端口组 {group_name} 已成功应用到设备 {device_name}",
                "device_name": device_name,
                "group_name": group_name,
                "applied_at": status.applied_at.isoformat()
            }
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def apply_address_group_to_all(self, group_name: str) -> Dict[str, Any]:
        """批量应用地址组配置到所有未配置的防火墙"""
        session = self.db.get_session()
        try:
            statuses = session.query(AddressGroupDeviceStatus).filter(
                AddressGroupDeviceStatus.group_name == group_name,
                AddressGroupDeviceStatus.status != "created"
            ).all()

            results = []
            for status in statuses:
                status.status = "created"
                status.applied_at = datetime.now()
                results.append({
                    "device_name": status.device_name,
                    "status": "success",
                    "message": f"地址组 {group_name} 已成功应用到设备 {status.device_name}"
                })

            session.commit()
            return {
                "status": "success",
                "group_name": group_name,
                "applied_count": len(results),
                "results": results
            }
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()

    def apply_port_group_to_all(self, group_name: str) -> Dict[str, Any]:
        """批量应用端口组配置到所有未配置的防火墙"""
        session = self.db.get_session()
        try:
            statuses = session.query(PortGroupDeviceStatus).filter(
                PortGroupDeviceStatus.group_name == group_name,
                PortGroupDeviceStatus.status != "created"
            ).all()

            results = []
            for status in statuses:
                status.status = "created"
                status.applied_at = datetime.now()
                results.append({
                    "device_name": status.device_name,
                    "status": "success",
                    "message": f"端口组 {group_name} 已成功应用到设备 {status.device_name}"
                })

            session.commit()
            return {
                "status": "success",
                "group_name": group_name,
                "applied_count": len(results),
                "results": results
            }
        except Exception as e:
            session.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            session.close()
