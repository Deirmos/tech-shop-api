from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from backend.core.exceptions.base import AppError

async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "code": exc.error_code,
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "message": "Внутренняя ошибка сервера",
            "code": "internal_server_error",
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "code": "http_exception",
        }
    )

def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
