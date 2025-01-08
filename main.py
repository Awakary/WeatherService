
from fastapi import FastAPI
from fastapi import Request
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.staticfiles import StaticFiles

from exceptions import OpenWeatherApiException
from router import router, templates

app = FastAPI()
app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )


app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)


@app.exception_handler(Exception)
async def http_exception_handler(request, exc: Exception):
    return templates.TemplateResponse(name='error.html',
                                      context={'request': request, "error": str(exc)})


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return templates.TemplateResponse(name='error.html',
                                      context={'request': request, "error": exc.detail})


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return templates.TemplateResponse(name='error.html',
                                      context={'request': request, "error": str(exc)})


@app.exception_handler(OpenWeatherApiException)
def open_weather_api_exception_handler(request: Request, exc: OpenWeatherApiException):
    return templates.TemplateResponse(name='error.html',
                                      context={'request': request, "error": exc.detail})




