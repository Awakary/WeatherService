
from fastapi import FastAPI
from fastapi import Request
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from router import router


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     return JSONResponse(
#         status_code=422,
#         content={"detail": '', "body": ''},
#     )
# @app.exception_handler(UsenameExistsException)
# def unicorn_exception_handler(request: Request, exc: UsenameExistsException):
#     return JSONResponse(
#         status_code=418,
#         content={"message": f"Oops! {exc.message} did something. There goes a rainbow..."},
#     )





