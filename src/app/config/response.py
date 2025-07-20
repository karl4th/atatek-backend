from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Any
from functools import wraps
from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    status: str = Field(..., example="success")
    version: str = Field(..., example="3.0.0")
    data: T

API_VERSION = "3.0.0"

def standard_success(data: Any):
    return {
        "status": "success",
        "version": API_VERSION,
        "data": data
    }


def autowrap(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        response: Response = kwargs.get("response")

        result = await func(*args, **kwargs)

        body = standard_success(result)

        # если response был передан и куки там есть — использовать его
        if response:
            response = JSONResponse(content=body, headers=response.headers)
            return response

        return JSONResponse(content=body)

    return wrapper


def standard_error(detail: Any, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "version": API_VERSION,
            "data": {
                "detail": detail
            }
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return standard_error(detail=exc.detail, status_code=exc.status_code)

