import re
from typing import Annotated

from fastapi import APIRouter, Request, Form, Depends, status, HTTPException
from fastapi import Response

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from authorazation.jwt_token import create_jwt_token, get_token
from authorazation.passwords import get_password_hash, authenticate_user, get_current_user, validate_password_username
from exceptions import UsernameExistsException, SameLocationException, NotSamePasswordException, \
    UsernamePasswordException, ExceptionWithMessage

from pd_models import UserInDB, FormData, LocationCheck, LocationCheckUser, FormDataCreate
from service import WeatherApiService
from sessions import UserDao, LocationDao
from utils import image_path, image_number

router = APIRouter()
templates = Jinja2Templates(directory='templates')

# Регистрация фильтров
templates.env.filters['image_path'] = image_path
templates.env.filters['image_number'] = image_number


@router.get('/')
def get_main_page(request: Request, response: Response):
    user_locations = []
    errors = []
    cookies_error_message = request.cookies.get('error_message')
    if cookies_error_message:
        errors.append(ExceptionWithMessage(status_code=400, detail=cookies_error_message))
    token = get_token(request)
    if token:
        try:
            user_locations = WeatherApiService().get_user_locations_with_weather(get_current_user(token))
        except Exception:
            errors.append(ExceptionWithMessage(status_code=500, detail="Ошибка API сервиса"))
    response = templates.TemplateResponse(name='index.html',
                                      context={'request': request, 'user_locations': user_locations,
                                               "errors": errors})
    response.delete_cookie(key="error_message")
    return response


@router.get('/locations')
async def get_locations_html(request: Request, city: str = None):
    errors = locations = []
    try:
        locations = WeatherApiService().find_locations_by_name(city=city)
    except Exception:
        errors.append(ExceptionWithMessage(status_code=500, detail="Ошибка API сервиса"))
        raise HTTPException(status_code=400, detail="User not found")
        # return templates.TemplateResponse(name='error.html',
        #                                   context={'request': request, "errors": errors})
    response = templates.TemplateResponse(name='locations.html',
                                          context={'request': request, 'locations': locations, "errors": errors})
    response.delete_cookie(key="error_message")
    return response


@router.post('/delete_location')
async def delete_locations(request: Request,  location_id: Annotated[int, Form()]):
    if LocationDao().delete_location_by_id(location_id) == "Удалено":
        return RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)


@router.get("/registration")
def get_reg_page(request: Request):
    return templates.TemplateResponse(name='registration.html',
                                      context={'request': request})


@router.post("/register")
def register_user(request: Request,  data: Annotated[FormDataCreate, Form()]
                  ):
    errors = validate_password_username(data, errors=[])
    hashed_password = get_password_hash(data.password)
    try:
        new_user = UserDao().save_user(data.login, hashed_password)
    except UsernameExistsException as e:
        errors.append(e)
    delattr(data, "repeated_password")
    if not errors:
        return login_for_access_token(login=data.login, password=data.password)
    return templates.TemplateResponse(name='registration.html',
                                      context={'request': request, "errors": errors})


@router.post("/token")
def login_for_access_token(login: str = Form(...), password: str = Form(...),
                           response=RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)):
    try:
        form_data = FormData(login=login, password=password)
        user = authenticate_user(form_data.login, form_data.password)
        access_token = create_jwt_token({"sub": user.login})
        # Если данные о пользователе получены, то мы генерируем JWT токен, а затем записываем его в cookies
        response.set_cookie(key="user_access_token", value=access_token, httponly=True)
        response.set_cookie(key="username", value=user.login, httponly=True)
        # response.delete_cookie(key="error_message")
        return response
    except HTTPException as e:
        response.set_cookie(key="error_message", value=e.detail, httponly=True)
        return response


@router.get("/users/me")
def get_user_me(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    return current_user


@router.post("/add_location")
def add_location_for_user_in_db(request: Request, data: Annotated[LocationCheck, Form()],
                                current_user: UserInDB = Depends(get_current_user),
                                response=RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)):
    location_dict = data.model_dump()
    lon = location_dict.pop("lon")
    lat = location_dict.pop("lat")
    location_for_db = LocationCheckUser(**location_dict,
                                        user_id=current_user.id, latitude=lat, longitude=lon)
    try:
        LocationDao().save_location(location_for_db)
    except SameLocationException as e:
        response.set_cookie(key="error_message", value=e.detail, httponly=True)
    return response


@router.post("/logout")
async def logout_user(response=RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)):
    response.delete_cookie(key="user_access_token")
    response.delete_cookie(key="username")
    return response

