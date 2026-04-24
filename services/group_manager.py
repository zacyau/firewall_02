from typing import Dict, List, Any, Optional
from database import Database, AddressGroup, PortGroup


class GroupManager:
    """组管理器 - 管理地址组和端口组"""

    def __init__(self, db: Database):
        self.db = db

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
