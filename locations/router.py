from typing import Annotated
from fastapi import APIRouter, Request, Form, Depends, status
from fastapi_cache.decorator import cache
from loguru import logger

from starlette.responses import RedirectResponse, HTMLResponse

from db.two_dao_shema import TwoDaoHelper
from templates.create_jinja import templates
from users.authorization.jwt_token import get_token
from users.authorization.passwords import get_current_user
from db.sessions import AbstractDao
from utilites.depends import get_weather_service, get_location_dao, get_location_service, get_two_dao
from locations.location_service import LocationService
from utilites.exceptions import SameLocationException
from fastapi_pagination import Page
from users.schemas import UserInDB, LocationCheck, WeatherCheck
from weather_service import WeatherApiService
from utilites.utils import ORHTMLCoder, custom_key_builder


location_router = APIRouter()


@location_router.get('/', response_model=Page[WeatherCheck], response_class=HTMLResponse)
def get_main_page(request: Request, current_page: int = None,  page: int = 1,
                  two_dao: TwoDaoHelper = Depends(get_two_dao),
                  weather_service: WeatherApiService = Depends(get_weather_service),
                  location_service: LocationService = Depends(get_location_service)):
    current_page = current_page if current_page else page
    paginated_user_locations = location_service.get_result_locations(page, get_token(request),
                                                                     two_dao, weather_service)
    response = templates.TemplateResponse(name='index.html',
                                          context={'request': request, 'current_page': current_page,
                                                   'saved_locations': paginated_user_locations,
                                                   "error": request.cookies.get('error_message')})
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
        redirect_url = f"/?current_page={current_page}"
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
