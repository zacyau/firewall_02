from fastapi import APIRouter, HTTPException
from services.config_manager import get_config_manager

router = APIRouter()
config_manager = get_config_manager()


@router.get("/devices", summary="获取所有设备")
async def get_all_devices():
    devices = config_manager.get_devices()
    device_list = list(devices.values())
    return {
        "status": "success",
        "count": len(device_list),
        "devices": device_list
    }


@router.post("/devices", summary="新增设备")
async def add_device(request: dict):
    name = request.get('name')
    if not name:
        raise HTTPException(status_code=400, detail="缺少设备名称 name")

    result = config_manager.add_device(name, request)
    if result.get('status') == 'success':
        return result
    raise HTTPException(status_code=400, detail=result.get('message'))


@router.post("/devices/validate", summary="验证设备配置")
async def validate_device_config(request: dict):
    result = config_manager.validate_device_config(request)
    return result


@router.get("/devices/export", summary="导出设备配置")
async def export_device_configs():
    devices = config_manager.export_to_dict()
    return {
        "status": "success",
        "count": len(devices),
        "devices": devices
    }


@router.post("/devices/seed", summary="重新导入配置种子")
async def reseed_devices():
    result = config_manager.seed_from_config()
    return result


@router.get("/devices/{device_name}", summary="获取单个设备信息")
async def get_device(device_name: str):
    device = config_manager.get_device(device_name)
    if device:
        return {
            "status": "success",
            "device": device
        }
    raise HTTPException(status_code=404, detail=f"设备 {device_name} 不存在")


@router.put("/devices/{device_name}", summary="更新设备配置")
async def update_device(device_name: str, request: dict):
    result = config_manager.update_device(device_name, request)
    if result.get('status') == 'success':
        return result
    raise HTTPException(status_code=400, detail=result.get('message'))


@router.delete("/devices/{device_name}", summary="删除设备")
async def delete_device(device_name: str):
    result = config_manager.delete_device(device_name)
    if result.get('status') == 'success':
        return result
    raise HTTPException(status_code=404, detail=result.get('message'))


@router.get("/devices/{device_name}/heartbeat", summary="检查设备心跳")
async def check_heartbeat(device_name: str):
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
