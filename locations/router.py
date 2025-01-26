from typing import Annotated
from fastapi import APIRouter, Request, Form, Depends, status, HTTPException
from fastapi_cache.decorator import cache
from loguru import logger

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from users.authorization.jwt_token import get_token
from users.authorization.passwords import get_current_user
from db.sessions import AbstractDao
from utilites.depends import get_weather_service, get_user_dao, get_location_dao, get_location_service
from locations.location_service import LocationService
from utilites.exceptions import SameLocationException

from users.schemas import UserInDB, LocationCheck
from weather_service import WeatherApiService
from utilites.utils import image_path, image_number, ORHTMLCoder, custom_key_builder

location_router = APIRouter()
templates = Jinja2Templates(directory='templates')


# Регистрация фильтров
templates.env.filters['image_path'] = image_path
templates.env.filters['image_number'] = image_number


@location_router.get('/')
def get_main_page(request: Request, current_page: int = None, page: int = 1,
                  user_dao: AbstractDao = Depends(get_user_dao),
                  loc_dao: AbstractDao = Depends(get_location_dao),
                  weather_service: WeatherApiService = Depends(get_weather_service),
                  location_service: LocationService = Depends(get_location_service)):
    token = get_token(request)
    data = location_service.get_result_locations(page, token, user_dao, loc_dao,
                                                 weather_service, current_page)
    response = templates.TemplateResponse(name='index.html',
                                          context={'request': request, 'current_page': data['current_page'],
                                                   'saved_locations': data['paginated_user_locations'],
                                                   "error": request.cookies.get('error_message'),
                                                   'total_pages': data['total_pages']})
    response.delete_cookie(key="error_message")
    return response


@location_router.get('/locations', dependencies=[Depends(get_current_user)])
@cache(expire=180, coder=ORHTMLCoder, key_builder=custom_key_builder)
async def get_locations_page(request: Request, city: str = None,
                             weather_service: WeatherApiService = Depends(get_weather_service)):
    locations = weather_service.find_locations_by_name(city=city)
    response = templates.TemplateResponse(name='locations.html',
                                          context={'request': request, 'locations': locations})
    response.delete_cookie(key="error_message")
    return response


@location_router.post('/delete_location', dependencies=[Depends(get_current_user)])
async def delete_locations(request: Request, location_id: Annotated[int, Form()],
                           location_name: Annotated[str, Form()], current_page: Annotated[int, Form()],
                           dao: AbstractDao = Depends(get_location_dao)):
    if dao.delete_one(location_id) == "Удалено":
        logger.info(f"Пользователь {request.cookies.get('username')} удалил локацию {location_name}")
        redirect_url = f"/?page={current_page}"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@location_router.post("/add_location", dependencies=[Depends(get_current_user)])
def add_location_for_user_in_db(request: Request, data: Annotated[LocationCheck, Form()],
                                current_user: UserInDB = Depends(get_current_user),
                                location_service: LocationService = Depends(get_location_service),
                                dao: AbstractDao = Depends(get_location_dao),
                                response=RedirectResponse('/', status_code=status.HTTP_303_SEE_OTHER)):
    location_for_db = location_service.get_location_db(data, current_user)
    try:
        location = dao.save_one(location_for_db)
        logger.info(f"Пользователь {request.cookies.get('username')} сохранил локацию {location.name}")
    except SameLocationException as e:
        response.set_cookie(key="error_message", value=e.detail, httponly=True)
    return response

