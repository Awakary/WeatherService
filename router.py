import re
from typing import Annotated

from fastapi import APIRouter, Request, Form, Depends, Response, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jinja2 import Environment, FileSystemLoader

from starlette.responses import FileResponse, RedirectResponse, JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from authorazation.jwt_token import create_jwt_token, get_token
from authorazation.passwords import get_password_hash, authenticate_user, get_current_user
from exceptions import UsernameExistsException, SameLocationException, NotSamePasswordException, \
    UsernamePasswordException

from pd_models import TokenCheck, UserInDB, FormData, LocationCheck, LocationCheckUser, FormDataCreate
from service import WeatherApiService
from sessions import UserDao, LocationDao
from utils import image_path, image_number

router = APIRouter()
templates = Jinja2Templates(directory='templates')

# Регистрация фильтра
templates.env.filters['image_path'] = image_path
templates.env.filters['image_number'] = image_number


@router.get('/')
def get_main_page(request: Request):
    user_locations = []
    errors = []
    token = get_token(request)
    if token:
        user_locations = WeatherApiService().get_user_locations_with_weather(get_current_user(token))
    return templates.TemplateResponse(name='index.html',
                                      context={'request': request, 'user_locations': user_locations,
                                               "errors": errors})


@router.get('/locations')
async def get_locations_html(request: Request, city: str = "Paris"):
    locations = WeatherApiService().find_locations_by_name(city=city)
    return templates.TemplateResponse(name='locations.html',
                                      context={'request': request, 'locations': locations})


@router.post('/delete_location')
async def delete_locations(request: Request,  location_id: Annotated[int, Form()]):
    if LocationDao().delete_location_by_id(location_id) == "Удалено":
        return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)


@router.get("/registration")
def get_reg_page(request: Request):
    return templates.TemplateResponse(name='registration.html',
                                      context={'request': request})


@router.post("/register")
def register_user(request: Request,  data: Annotated[FormDataCreate, Form()]):
    errors = []
    # Регулярное выражение для проверки, что строка содержит только латинские символы и цифры
    latin_regex = r'^[A-Za-z0-9]+$'
    if data.password != data.repeated_password:
        errors.append(NotSamePasswordException())
    elif (not re.match(latin_regex, data.login) or not re.match(latin_regex, data.password)
        or not re.match(latin_regex, data.repeated_password)):
        errors.append(UsernamePasswordException())
    hashed_password = get_password_hash(data.password)
    try:
        new_user = UserDao().save_user(data.login, hashed_password)

    except UsernameExistsException as e:
        errors.append(e)
    delattr(data, "repeated_password")
    if not errors:
        return login_for_access_token(form_data=data)
    return templates.TemplateResponse(name='registration.html',
                                      context={'request': request, "errors": errors})
    # return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)


@router.post("/token")
def login_for_access_token(form_data: Annotated[FormData, Form()],
                           response=RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)):
    user = authenticate_user(form_data.login, form_data.password)
    access_token = create_jwt_token({"sub": user.login})
    # Если данные о пользователе получены, то мы генерируем JWT токен, а затем записываем его в cookies
    response.set_cookie(key="user_access_token", value=access_token, httponly=True)
    response.set_cookie(key="username", value=user.login,  httponly=True)
    # return TokenCheck(access_token=access_token, token_type="bearer")
    return response


@router.get("/users/me")
def get_user_me(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    return current_user


@router.post("/add_location")
def add_location_for_user_in_db(request: Request, data: Annotated[LocationCheck, Form()],
                                current_user: UserInDB = Depends(get_current_user)):
    location_dict = data.model_dump()
    lon = location_dict.pop("lon")
    lat = location_dict.pop("lat")
    location_for_db = LocationCheckUser(**location_dict,
                                        user_id=current_user.id, latitude=lat, longitude=lon)
    try:
        LocationDao().save_location(location_for_db)
    except SameLocationException as e:
        return HTTPException(status_code=400, detail=e.message)
    return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout")
async def logout_user(response=RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)):
    response.delete_cookie(key="user_access_token")
    response.delete_cookie(key="username")
    return response

