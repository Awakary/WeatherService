from typing import Annotated
from fastapi import APIRouter, Request, Form, Depends, status, HTTPException

from starlette.responses import RedirectResponse

from templates.create_jinja import templates
from users.authorization.jwt_token import create_jwt_token
from users.authorization.passwords import get_password_hash, authenticate_user, validate_password_username
from db.sessions import AbstractDao
from utilites.depends import get_user_dao
from users.schemas import FormData, FormDataCreate

user_router = APIRouter()


@user_router.get('/authorization')
def get_authorization_page(request: Request):
    error = request.cookies.get('error_message')
    response = templates.TemplateResponse(name='search.html',
                                          context={'request': request, "error": error})
    response.delete_cookie(key="error_message")
    return response


@user_router.get("/registration")
def get_reg_page(request: Request):
    return templates.TemplateResponse(name='registration.html', context={'request': request})


@user_router.post("/register")
def register_user(request: Request, data: Annotated[FormDataCreate, Form()],
                  dao: AbstractDao = Depends(get_user_dao)):
    errors = validate_password_username(data, errors=[], dao=dao)
    if errors:
        return templates.TemplateResponse(name='registration.html',
                                          context={'request': request, "errors": errors})
    hashed_password = get_password_hash(data.password)
    dao.save_one(data.login, hashed_password)
    return RedirectResponse('/authorization', status_code=status.HTTP_303_SEE_OTHER)


@user_router.post("/token")
def login_for_access_token(login: str = Form(...), password: str = Form(...),
                           response=RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER),
                           dao: AbstractDao = Depends(get_user_dao)):
    try:
        form_data = FormData(login=login, password=password)
        user = authenticate_user(form_data.login, form_data.password, dao)
        access_token = create_jwt_token({"sub": user.login})
        response.set_cookie(key="user_access_token", value=access_token, httponly=True)
        response.set_cookie(key="username", value=user.login, httponly=True)
    except HTTPException as e:
        response.set_cookie(key="error_message", value=e.detail, httponly=True)
    return response


@user_router.post("/logout")
async def logout_user(response=RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)):
    response.delete_cookie(key="user_access_token")
    response.delete_cookie(key="username")
    return response
