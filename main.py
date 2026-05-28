from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from api.router import device_router, policy_router, address_group_router, port_group_router, log_router
from core.logger import logger
from core.exception_handler import global_exception_handler, http_exception_handler, validation_exception_handler
from database import Database
from services.config_manager import get_config_manager

app = FastAPI(
    title="防火墙自动化运维平台",
    description="多品牌防火墙统一管理平台 - 支持华为、山石、新华三、瞻博防火墙的策略自动化生成与下发",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(device_router, prefix="/api/v1", tags=["设备管理"])
app.include_router(policy_router, prefix="/api/v1", tags=["策略管理"])
app.include_router(address_group_router, prefix="/api/v1", tags=["地址组"])
app.include_router(port_group_router, prefix="/api/v1", tags=["端口组"])
app.include_router(log_router, prefix="/api/v1", tags=["系统日志"])


@app.on_event("startup")
async def startup_event():
    db = Database()
    db.create_tables()
    _migrate_add_action_column(db)
    _migrate_add_zones_column(db)
    logger.info("数据库初始化完成")

    cm = get_config_manager()
    result = cm.seed_from_config()
    logger.info(f"种子导入: {result['message']}")

    logger.info(f"已加载 {len(cm.get_devices())} 个设备配置")


def _migrate_add_action_column(db):
    try:
        from sqlalchemy import text
        session = db.get_session()
        result = session.execute(
            text("PRAGMA table_info(security_policies)")
        ).fetchall()
        columns = [row[1] for row in result]
        if 'action' not in columns:
            session.execute(
                text("ALTER TABLE security_policies ADD COLUMN action VARCHAR(20) DEFAULT 'permit'")
            )
            session.commit()
            logger.info("数据库迁移：已添加 security_policies.action 列")
        session.close()
    except Exception as e:
        logger.error(f"数据库迁移检查失败: {e}", exc_info=True)


def _migrate_add_zones_column(db):
    try:
        from sqlalchemy import text
        session = db.get_session()
        result = session.execute(
            text("PRAGMA table_info(firewall_devices)")
        ).fetchall()
        columns = [row[1] for row in result]
        if 'zones' not in columns:
            session.execute(
                text("ALTER TABLE firewall_devices ADD COLUMN zones JSON DEFAULT '{}'")
            )
            session.commit()
            logger.info("数据库迁移：已添加 firewall_devices.zones 列")
        if 'description' not in columns:
            session.execute(
                text("ALTER TABLE firewall_devices ADD COLUMN description VARCHAR(500) DEFAULT ''")
            )
            session.commit()
            logger.info("数据库迁移：已添加 firewall_devices.description 列")
        session.close()
    except Exception as e:
        logger.error(f"数据库迁移检查失败: {e}", exc_info=True)


@app.get("/", summary="首页")
async def root():
    cm = get_config_manager()
    return {
        "name": "防火墙自动化运维平台",
        "version": "1.0.0",
        "status": "running",
        "supported_vendors": ["huawei", "hillstone", "h3c", "juniper"],
        "features": [
            "设备配置管理（数据库驱动）",
            "Zone映射配置",
            "直连网段配置（CIDR）",
            "心跳检测",
            "防火墙路径计算",
            "策略自动生成",
            "策略下发执行"
        ],
        "device_count": len(cm.get_devices())
    }


@app.get("/health", summary="健康检查")
async def health_check():
    cm = get_config_manager()
    return {
        "status": "healthy",
        "service": "Firewall Automation Platform",
        "device_count": len(cm.get_devices())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
