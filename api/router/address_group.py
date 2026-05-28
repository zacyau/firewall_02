from fastapi import APIRouter, HTTPException
from api.models import AddressGroupRequest
from services import GroupManager
from database import Database

router = APIRouter()

db = Database()
group_manager = GroupManager(db)


@router.post("/groups/address", summary="创建地址组")
async def create_address_group(request: AddressGroupRequest):
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
    groups = group_manager.get_all_address_groups()
    return {
        "status": "success",
        "count": len(groups),
        "groups": groups
    }


@router.get("/groups/address/{group_name}", summary="获取地址组")
async def get_address_group(group_name: str):
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
    result = group_manager.delete_address_group(group_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=404, detail=result.get("message"))


@router.post("/groups/address/{group_name}/generate", summary="生成地址组配置")
async def generate_address_group_configs(group_name: str):
    result = group_manager.generate_address_group_configs(group_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.post("/groups/address/{group_name}/apply/{device_name}", summary="应用地址组配置到防火墙")
async def apply_address_group_config(group_name: str, device_name: str):
    result = group_manager.apply_address_group_config(group_name, device_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.post("/groups/address/{group_name}/apply-all", summary="批量应用地址组配置")
async def apply_address_group_to_all(group_name: str):
    result = group_manager.apply_address_group_to_all(group_name)
    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.get("/groups/address/{group_name}/status", summary="获取地址组配置状态")
async def get_address_group_status(group_name: str):
    statuses = group_manager.get_address_group_device_status(group_name)
    return {
        "status": "success",
        "group_name": group_name,
        "statuses": statuses
    }
