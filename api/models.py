from pydantic import BaseModel
from typing import Optional


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
    protocol: str
    dest_port: str


class PolicyApplyRequest(BaseModel):
    """策略应用请求"""
    device_name: str
    policy_script: str
    policy_id: Optional[int] = None
