from fastapi import APIRouter, HTTPException
from typing import List
from api.models import DeviceRegisterRequest, PolicyRequest, PolicyApplyRequest
from services import DeviceManager, PolicyManager
from database import Database

router = APIRouter()

db = Database()
device_manager = DeviceManager(db)
policy_manager = PolicyManager(db)


@router.post("/devices/register", summary="注册防火墙设备")
async def register_device(request: DeviceRegisterRequest):
    """注册新的防火墙设备"""
    device_config = request.dict()
    result = device_manager.register_device(device_config)

    if result.get("status") in ["registered", "updated"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.get("/devices", summary="获取所有设备")
async def get_all_devices():
    """获取所有注册的防火墙设备"""
    devices = device_manager.get_all_devices()
    return {
        "status": "success",
        "count": len(devices),
        "devices": devices
    }


@router.get("/devices/{device_name}", summary="获取单个设备信息")
async def get_device(device_name: str):
    """获取指定设备的信息"""
    device = device_manager.get_device(device_name)
    if device:
        return {
            "status": "success",
            "device": device
        }
    else:
        raise HTTPException(status_code=404, detail=f"设备 {device_name} 不存在")


@router.get("/devices/{device_name}/heartbeat", summary="检查设备心跳")
async def check_heartbeat(device_name: str):
    """检查指定防火墙设备的心跳状态"""
    result = device_manager.check_heartbeat(device_name)
    return result


@router.delete("/devices/{device_name}", summary="删除设备")
async def delete_device(device_name: str):
    """删除指定的防火墙设备"""
    result = device_manager.delete_device(device_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=404, detail=result.get("message"))


@router.post("/policies/generate", summary="生成防火墙策略")
async def generate_policy(request: PolicyRequest):
    """基于路径计算生成防火墙策略脚本

    输入：策略名、源IP、目的IP、协议、目标端口
    输出：需要配置的防火墙列表及每个防火墙的策略脚本
    """
    policy_config = request.dict()
    result = policy_manager.generate_policy(policy_config)

    return {
        "status": "success",
        "data": result
    }


@router.post("/policies/apply", summary="应用策略到防火墙")
async def apply_policy(request: PolicyApplyRequest):
    """将策略脚本应用到指定的防火墙设备"""
    policy_config = request.dict()
    result = policy_manager.apply_policy(policy_config)

    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.get("/policies", summary="获取所有策略")
async def get_all_policies():
    """获取所有已保存的策略"""
    policies = policy_manager.get_all_policies()
    return {
        "status": "success",
        "count": len(policies),
        "policies": policies
    }


@router.get("/policies/{policy_id}", summary="获取单个策略")
async def get_policy(policy_id: int):
    """获取指定策略的详细信息"""
    policy = policy_manager.get_policy(policy_id)
    if policy:
        return {
            "status": "success",
            "policy": policy
        }
    else:
        raise HTTPException(status_code=404, detail=f"策略 {policy_id} 不存在")
