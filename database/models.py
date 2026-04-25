from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class Database:
    """数据库管理类"""
    
    def __init__(self, db_url='sqlite:///./database/firewall_platform.db'):
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()
    
    def close(self):
        """关闭数据库连接"""
        self.engine.dispose()


class FirewallDevice(Base):
    """防火墙设备表 - 只保留直连网段和路由表"""
    __tablename__ = 'firewall_devices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    vendor = Column(String(50), nullable=False)
    ip = Column(String(50), nullable=False)
    port = Column(Integer, default=22)
    username = Column(String(50))
    password = Column(String(200))
    location = Column(String(200))
    
    connected_networks = Column(JSON)
    routing_table = Column(JSON)
    zone_mappings = Column(JSON)
    
    status = Column(String(20), default='offline')
    last_heartbeat = Column(DateTime, default=None)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "vendor": self.vendor,
            "ip": self.ip,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "location": self.location,
            "connected_networks": self.connected_networks or [],
            "routing_table": self.routing_table or [],
            "zone_mappings": self.zone_mappings or [],
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class SecurityPolicy(Base):
    """安全策略表"""
    __tablename__ = 'security_policies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_name = Column(String(100), nullable=False)
    source_ip = Column(String(50), nullable=False)
    dest_ip = Column(String(50), nullable=False)
    protocol = Column(String(10), nullable=False)
    dest_port = Column(String(50), nullable=False)
    source_zone = Column(String(50))
    dest_zone = Column(String(50))
    device_name = Column(String(100))
    policy_script = Column(Text)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "policy_name": self.policy_name,
            "source_ip": self.source_ip,
            "dest_ip": self.dest_ip,
            "protocol": self.protocol,
            "dest_port": self.dest_port,
            "source_zone": self.source_zone,
            "dest_zone": self.dest_zone,
            "device_name": self.device_name,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class PolicyAuditLog(Base):
    """策略审计日志表"""
    __tablename__ = 'policy_audit_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(Integer)
    action = Column(String(50), nullable=False)
    operator = Column(String(50))
    result = Column(String(20))
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "policy_id": self.policy_id,
            "action": self.action,
            "operator": self.operator,
            "result": self.result,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AddressGroup(Base):
    """地址组表 - 用于存储IP地址组"""
    __tablename__ = 'address_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    addresses = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "addresses": self.addresses or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class AddressGroupDeviceStatus(Base):
    """地址组设备配置状态表 - 记录各防火墙是否已配置该地址组"""
    __tablename__ = 'address_group_device_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String(100), nullable=False, index=True)
    device_name = Column(String(100), nullable=False, index=True)
    status = Column(String(20), default='pending')
    config_script = Column(Text)
    applied_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "group_name": self.group_name,
            "device_name": self.device_name,
            "status": self.status,
            "config_script": self.config_script,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class PortGroup(Base):
    """端口组表 - 用于存储端口组"""
    __tablename__ = 'port_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    ports = Column(JSON)
    protocol = Column(String(20), default='tcp')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "ports": self.ports or [],
            "protocol": self.protocol,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class PortGroupDeviceStatus(Base):
    """端口组设备配置状态表 - 记录各防火墙是否已配置该端口组"""
    __tablename__ = 'port_group_device_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_name = Column(String(100), nullable=False, index=True)
    device_name = Column(String(100), nullable=False, index=True)
    status = Column(String(20), default='pending')
    config_script = Column(Text)
    applied_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "group_name": self.group_name,
            "device_name": self.device_name,
            "status": self.status,
            "config_script": self.config_script,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
