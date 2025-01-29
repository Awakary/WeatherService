from config import settings
from fastapi_pagination import paginate, Page, Params

from db.two_dao_shema import TwoDaoHelper
from users.authorization import passwords as user_funcs
from users.schemas import LocationCheckUser, WeatherCheck, LocationCheck, UserInDB
from weather_service import WeatherApiService


class LocationService:

    @staticmethod
    def get_result_locations(page: int, token: str, two_dao: TwoDaoHelper,
                             weather_service: WeatherApiService) -> Page[WeatherCheck]:
        if token:
            current_user = user_funcs.get_current_user(token, two_dao.user)
            user_locations = two_dao.location.get_all(current_user)
            saved_locations = weather_service.get_user_locations_with_weather(user_locations=user_locations)
            paginated_user_locations = paginate(saved_locations, Params(page=page, size=settings.PAGE_SIZE))
            return paginated_user_locations

    @staticmethod
    def get_location_db(data: LocationCheck, current_user: UserInDB) -> LocationCheckUser:
        location_dict = data.model_dump()
        lon, lat = location_dict.pop("lon"), location_dict.pop("lat")
        location_for_db = LocationCheckUser(**location_dict, user_id=current_user.id,
                                            latitude=lat, longitude=lon)
        return location_for_db
