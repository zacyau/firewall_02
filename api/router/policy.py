from fastapi import APIRouter, HTTPException, Query
from api.models import PolicyApplyRequest, PolicyRequestWithGroups, PolicyValidateRequest
from services import PolicyManager
from services.policy_validator import PolicyValidator
from services.config_manager import get_config_manager
from database import Database

router = APIRouter()

db = Database()
policy_manager = PolicyManager(db)
policy_validator = PolicyValidator(db)
config_manager = get_config_manager()


@router.post("/policies/generate", summary="生成防火墙策略")
async def generate_policy(request: PolicyRequestWithGroups, dry_run: bool = Query(False, description="dry_run模式下仅验证不保存")):
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
        import traceback
        error_detail = str(e)
        error_trace = traceback.format_exc()
        return {
            "status": "error",
            "detail": error_detail,
            "traceback": error_trace
        }


@router.post("/policies/apply", summary="应用策略到防火墙")
async def apply_policy(request: PolicyApplyRequest, simulate: bool = Query(True, description="模拟模式：无真实设备时直接保存到数据库")):
    policy_config = request.dict()
    result = policy_manager.apply_policy(policy_config, simulate=simulate)

    if result.get("status") == "success":
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("message"))


@router.post("/policies/validate", summary="策略模拟验证")
async def validate_policies(request: PolicyValidateRequest):
    rules_data = [rule.dict() for rule in request.rules]
    report = policy_validator.validate_rules(
        device_name=request.device_id,
        direction=request.direction,
        rules=rules_data
    )
    return report


@router.get("/policies", summary="获取所有策略")
async def get_all_policies():
    policies = policy_manager.get_all_policies()
    return {
        "status": "success",
        "count": len(policies),
        "policies": policies
    }


@router.get("/policies/{policy_id}", summary="获取单个策略")
async def get_policy(policy_id: int):
    policy = policy_manager.get_policy(policy_id)
    if policy:
        return {
            "status": "success",
            "policy": policy
        }
    else:
        raise HTTPException(status_code=404, detail=f"策略 {policy_id} 不存在")
