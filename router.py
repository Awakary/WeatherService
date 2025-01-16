from typing import Annotated
from fastapi import APIRouter, Request, Form, Depends, status, HTTPException
from loguru import logger

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from authorization.jwt_token import create_jwt_token, get_token
from authorization.passwords import get_password_hash, authenticate_user, get_current_user, validate_password_username
from utilites.exceptions import UsernameExistsException, SameLocationException

from pd_models import UserInDB, FormData, LocationCheck, LocationCheckUser, FormDataCreate
from service import WeatherApiService
from db.sessions import UserDao, LocationDao
from utilites.utils import image_path, image_number, get_paginated_locations_and_total_pages

router = APIRouter()
templates = Jinja2Templates(directory='templates')
weather_service = WeatherApiService()

user_dao = UserDao()
location_dao = LocationDao()


# Регистрация фильтров
templates.env.filters['image_path'] = image_path
templates.env.filters['image_number'] = image_number


@router.get('/authorization')
def get_autorization_page(request: Request):
    error = request.cookies.get('error_message')
    response = templates.TemplateResponse(name='search.html',
                                          context={'request': request, "error": error})
    response.delete_cookie(key="error_message")
    return response


@router.get('/')
def get_main_page(request: Request, current_page: int = None, page: int = 1):
    paginated_user_locations = []
    total_pages = 0
    current_page = current_page if current_page else page
    token = get_token(request)
    if token:
        user_locations = weather_service.get_user_locations_with_weather(get_current_user(token))
        paginated_user_locations, total_pages = get_paginated_locations_and_total_pages(user_locations, page)
    response = templates.TemplateResponse(name='index.html',
                                          context={'request': request, 'user_locations': paginated_user_locations,
                                                   "error": request.cookies.get('error_message'),
                                                   'total_pages': total_pages, 'current_page': current_page})
    response.delete_cookie(key="error_message")
    return response


@router.get('/locations')
async def get_locations_html(request: Request, city: str = None,
                             current_user: UserInDB = Depends(get_current_user)):
    locations = weather_service.find_locations_by_name(city=city)
    response = templates.TemplateResponse(name='locations.html',
                                          context={'request': request, 'locations': locations})
    response.delete_cookie(key="error_message")
    return response


@router.post('/delete_location')
async def delete_locations(request: Request, location_id: Annotated[int, Form()],
                           location_name: Annotated[str, Form()], current_page: Annotated[int, Form()]):
    if location_dao.delete_one(location_id) == "Удалено":
        logger.info(f"Пользователь {request.cookies.get('username')} удалил локацию {location_name}")
        redirect_url = f"/?page={current_page}"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/registration")
def get_reg_page(request: Request):
    return templates.TemplateResponse(name='registration.html', context={'request': request})


@router.post("/register")
def register_user(request: Request, data: Annotated[FormDataCreate, Form()]):
    errors = validate_password_username(data, errors=[])
    if errors:
        return templates.TemplateResponse(name='registration.html',
                                          context={'request': request, "errors": errors})
    hashed_password = get_password_hash(data.password)
    user_dao.save_one(data.login, hashed_password)
    delattr(data, "repeated_password")
    if not errors:
        return RedirectResponse('/authorization', status_code=status.HTTP_303_SEE_OTHER)



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
        return response
    except HTTPException as e:
        response.set_cookie(key="error_message", value=e.detail, httponly=True)
        return response


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
        location_dao.save_one(location_for_db)
        logger.info(f"Пользователь {request.cookies.get('username')} сохранил локацию {location_dict.get('name')}")
    except SameLocationException as e:
        response.set_cookie(key="error_message", value=e.detail, httponly=True)
    return response


@router.post("/logout")
async def logout_user(response=RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)):
    response.delete_cookie(key="user_access_token")
    response.delete_cookie(key="username")
    return response
