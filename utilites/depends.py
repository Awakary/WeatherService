from db.two_dao_shema import TwoDaoHelper
from db.models import User, Location
from db.sessions import UserDao, LocationDao
from locations.location_service import LocationService
from weather_service import WeatherApiService


def get_user_dao() -> UserDao:
    return UserDao(model=User)


def get_location_dao() -> LocationDao:
    return LocationDao(model=Location)


def get_weather_service() -> WeatherApiService:
    return WeatherApiService()


def get_location_service() -> LocationService:
    return LocationService()


def get_two_dao() -> TwoDaoHelper:
    return TwoDaoHelper(user=UserDao(model=User), location=LocationDao(model=Location))
