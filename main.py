from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
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

app.include_router(router, prefix="/api/v1", tags=["防火墙管理"])


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    db = Database()
    db.create_tables()
    _migrate_add_action_column(db)
    _migrate_add_zones_column(db)
    print("数据库初始化完成")

    # 从配置文件种子导入（仅数据库为空时执行）
    cm = get_config_manager()
    result = cm.seed_from_config()
    print(f"种子导入: {result['message']}")

    print(f"已加载 {len(cm.get_devices())} 个设备配置")


def _migrate_add_action_column(db):
    """迁移：为 security_policies 表添加 action 列"""
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
            print("数据库迁移：已添加 security_policies.action 列")
        session.close()
    except Exception as e:
        print(f"数据库迁移检查：{e}")


def _migrate_add_zones_column(db):
    """迁移：为 firewall_devices 表添加 zones 列"""
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
            print("数据库迁移：已添加 firewall_devices.zones 列")
        if 'description' not in columns:
            session.execute(
                text("ALTER TABLE firewall_devices ADD COLUMN description VARCHAR(500) DEFAULT ''")
            )
            session.commit()
            print("数据库迁移：已添加 firewall_devices.description 列")
        session.close()
    except Exception as e:
        print(f"数据库迁移检查：{e}")


@app.get("/", summary="首页")
async def root():
    """平台首页"""
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
    """健康检查接口"""
    cm = get_config_manager()
    return {
        "status": "healthy",
        "service": "Firewall Automation Platform",
        "device_count": len(cm.get_devices())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
