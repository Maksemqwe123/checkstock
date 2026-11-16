from fastapi import HTTPException

from checkstock_backend.api.utils.exceptions import (
    AppError,
    IdempotencyConflictError,
    InsufficientStockError,
    NotFoundError,
)


def http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, InsufficientStockError):
        return HTTPException(409, detail={"code": exc.code, "message": exc.message})
    if isinstance(exc, IdempotencyConflictError):
        return HTTPException(409, detail={"code": exc.code, "message": exc.message})
    if isinstance(exc, NotFoundError):
        return HTTPException(404, detail={"code": exc.code, "message": exc.message})
    if isinstance(exc, AppError):
        return HTTPException(400, detail={"code": exc.code, "message": exc.message})
    return HTTPException(400, detail=str(exc))


def merge_idempotency(body_key: str | None, header: str | None) -> str | None:
    return body_key or header