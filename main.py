from fastapi import FastAPI
from src.app.config.response import http_exception_handler
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.app import init_app

app = FastAPI(
    title="ATATEK - онлайн шежіре",
    version="3.0.0",
    description="Жаңа нұсқа жаңа фреймворкта FastAPI",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://alash.atatek.kz"],  # Разрешаем фронтенду на Next.js делать запросы
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Обработка HTTP ошибок
app.add_exception_handler(HTTPException, http_exception_handler)

# Обработка ошибок валидации (например, pydantic)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "version": "3.0.0",
            "data": {"detail": exc.errors()}
        }
    )


init_app(app)