from pydantic import BaseModel
from typing import Optional, List


class DeviceRegisterRequest(BaseModel):
    """设备注册请求"""
    name: str
    vendor: str
    ip: str
    port: Optional[int] = 22
    username: Optional[str] = None
    password: Optional[str] = None
    location: Optional[str] = None
    connected_networks: Optional[list] = []
    routing_table: Optional[list] = []


class PolicyRequest(BaseModel):
    """策略请求"""
    policy_name: str
    source_ip: str
    dest_ip: str
    protocol: str = 'tcp'
    dest_port: str
    description: Optional[str] = None


class PolicyApplyRequest(BaseModel):
    """策略应用请求"""
    device_name: str
    policy_script: str
    policy_name: Optional[str] = None
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    protocol: Optional[str] = 'tcp'
    dest_port: Optional[str] = None
    source_zone: Optional[str] = None
    dest_zone: Optional[str] = None
    action: Optional[str] = 'permit'
    policy_id: Optional[int] = None


class AddressGroupRequest(BaseModel):
    """地址组请求"""
    name: str
    description: Optional[str] = None
    addresses: list = []


class PortGroupRequest(BaseModel):
    """端口组请求"""
    name: str
    description: Optional[str] = None
    ports: list = []
    protocol: Optional[str] = 'tcp'


class PolicyRequestWithGroups(BaseModel):
    """基于组的策略请求"""
    policy_name: str
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    source_group: Optional[str] = None
    dest_group: Optional[str] = None
    port_group: Optional[str] = None
    protocol: str = 'tcp'


class PolicyRuleItem(BaseModel):
    """策略规则项"""
    source_ip: str
    dest_ip: str
    protocol: str = 'tcp'
    dest_port: str = 'any'
    action: str = 'permit'
    source_zone: Optional[str] = None
    dest_zone: Optional[str] = None


class PolicyValidateRequest(BaseModel):
    """策略验证请求"""
    device_id: str
    direction: str
    rules: List[PolicyRuleItem]
