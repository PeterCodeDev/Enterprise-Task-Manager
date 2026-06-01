from typing import Any, Dict

from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, status_code: int, detail: str, extra: Dict[str, Any] = None):
        self.status_code = status_code
        self.detail = detail
        self.extra = extra or {}


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(status_code=403, detail=detail)


class ConflictException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=409, detail=detail)


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, **exc.extra},
    )


async def validation_exception_handler(request: Request, exc):
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors},
    )


async def general_exception_handler(request: Request, exc: Exception):
    from app.logging_config import logger
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
