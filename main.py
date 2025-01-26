from fastapi import FastAPI
from fastapi import Request
from loguru import logger
from pydantic import ValidationError
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from redis import asyncio as aioredis

from config import settings
from locations.router import location_router, templates
from users.router import user_router
from utilites.exceptions import OpenWeatherApiException, TokenExpiredException

app = FastAPI()


logger.add("logs/{time:DD-MM-YYYY}.log", rotation="1 MB")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router)
app.include_router(location_router)


@app.on_event("startup")
async def startup():
   redis = aioredis.from_url(f"redis://{settings.POSTGRES_HOST}", encoding="utf8", decode_responses=True)
   FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


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


@app.exception_handler(TokenExpiredException)
def open_weather_api_exception_handler(request: Request, exc: TokenExpiredException):
    logger.error(f"Запрос: {request.method} {request.url} - ошибка {exc.detail}")
    response = RedirectResponse('/authorization', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="error_message", value=exc.detail, httponly=True)
    response.delete_cookie(key="user_access_token")
    return response


# @app.exception_handler(Exception)
# async def http_exception_handler(request, exc: Exception):
#     logger.error(f"Запрос: {request.method} {request.url} - ошибка {str(exc)}")
#     return templates.TemplateResponse(name='error.html',
#                                       context={'request': request, "error": str(exc)})
