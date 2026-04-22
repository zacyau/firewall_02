from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from database import Database
from services.config_loader import config_loader

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
    print("数据库初始化完成")

    print(f"已加载 {len(config_loader.get_devices())} 个设备配置")


@app.get("/", summary="首页")
async def root():
    """平台首页"""
    return {
        "name": "防火墙自动化运维平台",
        "version": "1.0.0",
        "status": "running",
        "supported_vendors": ["huawei", "hillstone", "h3c", "juniper"],
        "features": [
            "设备配置管理（Web界面）",
            "Zone映射配置",
            "直连网段配置",
            "路由表配置",
            "心跳检测",
            "防火墙路径计算",
            "策略自动生成",
            "策略下发执行"
        ]
    }


@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "Firewall Automation Platform",
        "device_count": len(config_loader.get_devices())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
