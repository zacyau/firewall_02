import os
from fastapi import APIRouter, HTTPException, Query
from core.logger import LOG_FILE, LOG_DIR

router = APIRouter()


@router.get("/logs", summary="获取系统日志")
async def get_logs(
    lines: int = Query(200, description="获取最后N行日志"),
    level: str = Query(None, description="按日志级别过滤: DEBUG/INFO/WARNING/ERROR"),
    keyword: str = Query(None, description="关键词搜索")
):
    if not os.path.exists(LOG_FILE):
        return {
            "status": "success",
            "lines": [],
            "total": 0,
            "file": LOG_FILE
        }

    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取日志文件失败: {str(e)}")

    result_lines = all_lines[-lines:] if lines < len(all_lines) else all_lines

    if level:
        level_upper = level.upper()
        result_lines = [l for l in result_lines if f" {level_upper} " in l]

    if keyword:
        result_lines = [l for l in result_lines if keyword.lower() in l.lower()]

    return {
        "status": "success",
        "lines": [l.rstrip('\n') for l in result_lines],
        "total": len(result_lines),
        "file": LOG_FILE
    }


@router.delete("/logs", summary="清空日志文件")
async def clear_logs():
    if not os.path.exists(LOG_FILE):
        return {"status": "success", "message": "日志文件不存在"}

    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.truncate(0)
        return {"status": "success", "message": "日志已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空日志失败: {str(e)}")


@router.get("/logs/info", summary="获取日志文件信息")
async def get_log_info():
    file_size = 0
    if os.path.exists(LOG_FILE):
        file_size = os.path.getsize(LOG_FILE)

    backup_count = 0
    if os.path.exists(LOG_DIR):
        backup_count = len([f for f in os.listdir(LOG_DIR) if f.startswith('app.log.')])

    return {
        "status": "success",
        "file": LOG_FILE,
        "file_size": file_size,
        "file_size_mb": round(file_size / (1024 * 1024), 2),
        "backup_count": backup_count,
        "max_size_mb": 5,
        "max_backups": 5
    }
