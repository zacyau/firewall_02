from fastapi import APIRouter, HTTPException, Query
from api.models import DeviceRegisterRequest, PolicyApplyRequest, AddressGroupRequest, PortGroupRequest, PolicyRequestWithGroups, PolicyValidateRequest
from services import PolicyManager, GroupManager
from services.policy_validator import PolicyValidator
from services.config_manager import config_manager
from database import Database

router = APIRouter()

db = Database()
policy_manager = PolicyManager(db)
group_manager = GroupManager(db)
policy_validator = PolicyValidator(db)


@router.post("/devices/register", summary="注册防火墙设备")
async def register_device(request: DeviceRegisterRequest):
    """注册新的防火墙设备（通过配置文件）"""
    device_config = request.dict()
    name = device_config.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="缺少设备名称 name")

    result = config_manager.add_device(name, device_config)
    if result.get('status') == 'success':
        return result
    raise HTTPException(status_code=400, detail=result.get('message'))


@router.get("/devices", summary="获取所有设备")
async def get_all_devices():
    """获取所有注册的防火墙设备"""
    devices = config_manager.get_devices()
    device_list = list(devices.values())
    return {
        "status": "success",
        "count": len(device_list),
        "devices": device_list
    }


@router.get("/devices/{device_name}", summary="获取单个设备信息")
async def get_device(device_name: str):
    """获取指定设备的信息"""
    device = config_manager.get_device(device_name)
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
    device = config_manager.get_device(device_name)
    if not device:
        raise HTTPException(status_code=404, detail=f"设备 {device_name} 不存在")

    try:
        from factory import FirewallFactory
        factory = FirewallFactory()
        adapter = factory.create_firewall(device)
        return adapter.check_heartbeat()
    except Exception as e:
        return {
            "status": "error",
            "device_name": device_name,
            "message": str(e)
        }


@router.delete("/devices/{device_name}", summary="删除设备")
async def delete_device(device_name: str):
    """删除指定的防火墙设备"""
    result = config_manager.delete_device(device_name)
    if result.get('status') == 'success':
        return result
    raise HTTPException(status_code=404, detail=result.get('message'))


@router.post("/policies/generate", summary="生成防火墙策略")
async def generate_policy(request: PolicyRequestWithGroups, dry_run: bool = Query(False, description="dry_run模式下仅验证不保存")):
    """基于路径计算生成防火墙策略脚本

    输入：策略名、源地址组、目的地址组、端口组
    输出：需要配置的防火墙列表及每个防火墙的策略脚本

    当 dry_run=true 时，自动对生成的策略进行冲突检测和冗余分析，不将策略标记为"待下发"
    """
    import traceback
    try:
        policy_config = request.dict(exclude_none=True)
        result = policy_manager.generate_policy(policy_config)

        if dry_run and result.get("status") != "error":
            validation_report = policy_validator.validate_generated_policies(result)
            result["validation"] = validation_report

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
async def apply_policy(request: PolicyApplyRequest, simulate: bool = Query(True, description="模拟模式：无真实设备时直接保存到数据库")):
    """将策略脚本应用到指定的防火墙设备
    
    参数：
    - simulate: true（默认）为模拟模式，直接保存到数据库，不连接真实设备
    - simulate: false 为真实模式，连接防火墙设备并下发配置
    """
    policy_config = request.dict()
    result = policy_manager.apply_policy(policy_config, simulate=simulate)

    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.post("/policies/validate", summary="策略模拟验证")
async def validate_policies(request: PolicyValidateRequest):
    """对策略规则进行冲突检测和冗余分析

    在策略正式下发前，对新生成的防火墙策略规则进行全面验证，
    自动检测潜在的规则冲突和冗余情况，生成结构化验证报告。

    请求参数：
    - device_id: 目标防火墙设备的唯一标识符（设备名称）
    - direction: 策略方向，inbound 或 outbound
    - rules: 待验证的策略规则列表
    """
    rules_data = [rule.dict() for rule in request.rules]
    report = policy_validator.validate_rules(
        device_name=request.device_id,
        direction=request.direction,
        rules=rules_data
    )
    return report


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


@router.post("/groups/address/{group_name}/generate", summary="生成地址组配置")
async def generate_address_group_configs(group_name: str):
    """生成地址组在所有防火墙上的配置脚本"""
    result = group_manager.generate_address_group_configs(group_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.post("/groups/address/{group_name}/apply/{device_name}", summary="应用地址组配置到防火墙")
async def apply_address_group_config(group_name: str, device_name: str):
    """应用地址组配置到指定防火墙"""
    result = group_manager.apply_address_group_config(group_name, device_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.post("/groups/address/{group_name}/apply-all", summary="批量应用地址组配置")
async def apply_address_group_to_all(group_name: str):
    """批量应用地址组配置到所有未配置的防火墙"""
    result = group_manager.apply_address_group_to_all(group_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.get("/groups/address/{group_name}/status", summary="获取地址组配置状态")
async def get_address_group_status(group_name: str):
    """获取地址组在各防火墙上的配置状态"""
    statuses = group_manager.get_address_group_device_status(group_name)
    return {
        "status": "success",
        "group_name": group_name,
        "statuses": statuses
    }


@router.post("/groups/port/{group_name}/generate", summary="生成端口组配置")
async def generate_port_group_configs(group_name: str):
    """生成端口组在所有防火墙上的配置脚本"""
    result = group_manager.generate_port_group_configs(group_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.post("/groups/port/{group_name}/apply/{device_name}", summary="应用端口组配置到防火墙")
async def apply_port_group_config(group_name: str, device_name: str):
    """应用端口组配置到指定防火墙"""
    result = group_manager.apply_port_group_config(group_name, device_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.post("/groups/port/{group_name}/apply-all", summary="批量应用端口组配置")
async def apply_port_group_to_all(group_name: str):
    """批量应用端口组配置到所有未配置的防火墙"""
    result = group_manager.apply_port_group_to_all(group_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.get("/groups/port/{group_name}/status", summary="获取端口组配置状态")
async def get_port_group_status(group_name: str):
    """获取端口组在各防火墙上的配置状态"""
    statuses = group_manager.get_port_group_device_status(group_name)
    return {
        "status": "success",
        "group_name": group_name,
        "statuses": statuses
    }


# ==================== 配置文件管理 API ====================

@router.get("/config/devices", summary="获取所有设备配置")
async def get_all_device_configs():
    """获取所有设备配置（从配置文件）"""
    devices = config_manager.get_devices()
    return {
        "status": "success",
        "count": len(devices),
        "devices": devices
    }


@router.get("/config/devices/{device_name}", summary="获取单个设备配置")
async def get_device_config(device_name: str):
    """获取指定设备的配置"""
    device = config_manager.get_device(device_name)
    if device:
        return {
            "status": "success",
            "device": device
        }
    raise HTTPException(status_code=404, detail=f"设备 {device_name} 不存在")


@router.put("/config/devices/{device_name}", summary="更新设备配置")
async def update_device_config(device_name: str, request: dict):
    """更新指定设备的配置"""
    result = config_manager.update_device(device_name, request)
    if result.get('status') == 'success':
        return result
    raise HTTPException(status_code=400, detail=result.get('message'))


@router.post("/config/devices", summary="新增设备配置")
async def add_device_config(request: dict):
    """新增设备配置"""
    name = request.get('name')
    if not name:
        raise HTTPException(status_code=400, detail="缺少设备名称 name")

    result = config_manager.add_device(name, request)
    if result.get('status') == 'success':
        return result
    raise HTTPException(status_code=400, detail=result.get('message'))


@router.delete("/config/devices/{device_name}", summary="删除设备配置")
async def delete_device_config(device_name: str):
    """删除设备配置"""
    result = config_manager.delete_device(device_name)
    if result.get('status') == 'success':
        return result
    raise HTTPException(status_code=400, detail=result.get('message'))


@router.post("/config/devices/backup", summary="备份配置文件")
async def backup_config():
    """手动创建配置文件备份"""
    result = config_manager.create_backup()
    if result.get('status') == 'success':
        return result
    raise HTTPException(status_code=400, detail=result.get('message'))


@router.post("/config/devices/validate", summary="验证设备配置")
async def validate_device_config(request: dict):
    """验证设备配置格式"""
    result = config_manager.validate_device_config(request)
    return result
