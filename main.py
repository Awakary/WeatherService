from fastapi import FastAPI
from fastapi import Request
from loguru import logger
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware

from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles

from router import router, templates
from exceptions import OpenWeatherApiException


app = FastAPI()

logger.add("app_logs.log", rotation="1 MB")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    logger.error(f"Запрос: {request.method} {request.url} - ошибка {exc.detail}")
    return templates.TemplateResponse(name='error.html',
                                      context={'request': request, "error": exc.detail})


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(f"Запрос: {request.method} {request.url} - ошибка {str(exc)}")
    return templates.TemplateResponse(name='error.html',
                                      context={'request': request, "error": str(exc)})


@app.exception_handler(OpenWeatherApiException)
def open_weather_api_exception_handler(request: Request, exc: OpenWeatherApiException):
    logger.error(f"Запрос: {request.method} {request.url} - ошибка {exc.detail}")
    return templates.TemplateResponse(name='error.html',
                                      context={'request': request, "error": exc.detail})


@app.exception_handler(Exception)
async def http_exception_handler(request, exc: Exception):
    logger.error(f"Запрос: {request.method} {request.url} - ошибка {str(exc)}")
    return templates.TemplateResponse(name='error.html',
                                      context={'request': request, "error": str(exc)})
