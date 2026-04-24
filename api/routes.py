from fastapi import APIRouter, HTTPException
from typing import List
from api.models import DeviceRegisterRequest, PolicyRequest, PolicyApplyRequest, AddressGroupRequest, PortGroupRequest, PolicyRequestWithGroups
from services import DeviceManager, PolicyManager, GroupManager
from database import Database

router = APIRouter()

db = Database()
device_manager = DeviceManager(db)
policy_manager = PolicyManager(db)
group_manager = GroupManager(db)


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
async def generate_policy(request: PolicyRequestWithGroups):
    """基于路径计算生成防火墙策略脚本

    输入：策略名、源地址组、目的地址组、端口组
    输出：需要配置的防火墙列表及每个防火墙的策略脚本
    """
    import traceback
    try:
        policy_config = request.dict(exclude_none=True)
        result = policy_manager.generate_policy(policy_config)

        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        error_detail = str(e)
        error_trace = traceback.format_exc()
        print(f"ERROR in generate_policy: {error_detail}")
        print(error_trace)
        return {
            "status": "error",
            "detail": error_detail
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


@router.post("/groups/address", summary="创建地址组")
async def create_address_group(request: AddressGroupRequest):
    """创建新的地址组"""
    result = group_manager.create_address_group(
        name=request.name,
        addresses=request.addresses,
        description=request.description
    )
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.get("/groups/address", summary="获取所有地址组")
async def get_all_address_groups():
    """获取所有地址组"""
    groups = group_manager.get_all_address_groups()
    return {
        "status": "success",
        "count": len(groups),
        "groups": groups
    }


@router.get("/groups/address/{group_name}", summary="获取地址组")
async def get_address_group(group_name: str):
    """获取指定地址组"""
    group = group_manager.get_address_group(group_name)
    if group:
        return {
            "status": "success",
            "group": group
        }
    else:
        raise HTTPException(status_code=404, detail=f"地址组 {group_name} 不存在")


@router.put("/groups/address/{group_name}", summary="更新地址组")
async def update_address_group(group_name: str, request: AddressGroupRequest):
    """更新地址组"""
    result = group_manager.update_address_group(
        name=group_name,
        addresses=request.addresses,
        description=request.description
    )
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=404, detail=result.get("message"))


@router.delete("/groups/address/{group_name}", summary="删除地址组")
async def delete_address_group(group_name: str):
    """删除地址组"""
    result = group_manager.delete_address_group(group_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=404, detail=result.get("message"))


@router.post("/groups/port", summary="创建端口组")
async def create_port_group(request: PortGroupRequest):
    """创建新的端口组"""
    result = group_manager.create_port_group(
        name=request.name,
        ports=request.ports,
        protocol=request.protocol,
        description=request.description
    )
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.get("/groups/port", summary="获取所有端口组")
async def get_all_port_groups():
    """获取所有端口组"""
    groups = group_manager.get_all_port_groups()
    return {
        "status": "success",
        "count": len(groups),
        "groups": groups
    }


@router.get("/groups/port/{group_name}", summary="获取端口组")
async def get_port_group(group_name: str):
    """获取指定端口组"""
    group = group_manager.get_port_group(group_name)
    if group:
        return {
            "status": "success",
            "group": group
        }
    else:
        raise HTTPException(status_code=404, detail=f"端口组 {group_name} 不存在")


@router.put("/groups/port/{group_name}", summary="更新端口组")
async def update_port_group(group_name: str, request: PortGroupRequest):
    """更新端口组"""
    result = group_manager.update_port_group(
        name=group_name,
        ports=request.ports,
        protocol=request.protocol,
        description=request.description
    )
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=404, detail=result.get("message"))


@router.delete("/groups/port/{group_name}", summary="删除端口组")
async def delete_port_group(group_name: str):
    """删除端口组"""
    result = group_manager.delete_port_group(group_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=404, detail=result.get("message"))
