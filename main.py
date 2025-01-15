from fastapi import FastAPI
from fastapi import Request
from loguru import logger
from pydantic import ValidationError
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from router import router, templates
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


@app.exception_handler(TokenExpiredException)
def open_weather_api_exception_handler(request: Request, exc: TokenExpiredException):
    logger.error(f"Запрос: {request.method} {request.url} - ошибка {exc.detail}")
    response = RedirectResponse('/authorization', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="error_message", value=exc.detail, httponly=True)
    response.delete_cookie(key="user_access_token")
    return response


@app.exception_handler(Exception)
async def http_exception_handler(request, exc: Exception):
    logger.error(f"Запрос: {request.method} {request.url} - ошибка {str(exc)}")
    return templates.TemplateResponse(name='error.html',
                                      context={'request': request, "error": str(exc)})
