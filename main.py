
from fastapi import FastAPI
from fastapi import Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.staticfiles import StaticFiles

from router import router, templates

app = FastAPI()
app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
     errors = []
     print(1)
     return templates.TemplateResponse(name='error.html',
                                       context={'request': request, "errors": errors})

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)


@app.exception_handler(Exception)
async def http_exception_handler(request, exc: Exception):
     errors = []
     print(1)
     return templates.TemplateResponse(name='error.html',
                                       context={'request': request, "errors": errors})


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





