from fastapi import APIRouter, HTTPException
from api.models import PortGroupRequest
from services import GroupManager
from database import Database

router = APIRouter()

db = Database()
group_manager = GroupManager(db)


@router.post("/groups/port", summary="创建端口组")
async def create_port_group(request: PortGroupRequest):
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
    groups = group_manager.get_all_port_groups()
    return {
        "status": "success",
        "count": len(groups),
        "groups": groups
    }


@router.get("/groups/port/{group_name}", summary="获取端口组")
async def get_port_group(group_name: str):
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
    result = group_manager.delete_port_group(group_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=404, detail=result.get("message"))


@router.post("/groups/port/{group_name}/generate", summary="生成端口组配置")
async def generate_port_group_configs(group_name: str):
    result = group_manager.generate_port_group_configs(group_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.post("/groups/port/{group_name}/apply/{device_name}", summary="应用端口组配置到防火墙")
async def apply_port_group_config(group_name: str, device_name: str):
    result = group_manager.apply_port_group_config(group_name, device_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.post("/groups/port/{group_name}/apply-all", summary="批量应用端口组配置")
async def apply_port_group_to_all(group_name: str):
    result = group_manager.apply_port_group_to_all(group_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.get("/groups/port/{group_name}/status", summary="获取端口组配置状态")
async def get_port_group_status(group_name: str):
    statuses = group_manager.get_port_group_device_status(group_name)
    return {
        "status": "success",
        "group_name": group_name,
        "statuses": statuses
    }
