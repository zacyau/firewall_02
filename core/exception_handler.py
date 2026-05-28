import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from core.logger import logger


async def global_exception_handler(request: Request, exc: Exception):
    error_trace = traceback.format_exc()
    logger.error(
        f"未捕获异常 [{request.method}] {request.url}: {str(exc)}\n{error_trace}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": str(exc),
            "traceback": error_trace
        }
    )


async def http_exception_handler(request: Request, exc):
    logger.warning(
        f"HTTP异常 [{request.method}] {request.url}: {exc.status_code} - {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def validation_exception_handler(request: Request, exc):
    errors = str(exc.errors()) if hasattr(exc, 'errors') else str(exc)
    logger.warning(
        f"请求验证异常 [{request.method}] {request.url}: {errors}"
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors() if hasattr(exc, 'errors') else str(exc)}
    )
