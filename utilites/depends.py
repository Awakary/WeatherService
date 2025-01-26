from db.models import User, Location
from db.sessions import UserDao, LocationDao
from locations.location_service import LocationService
from weather_service import WeatherApiService


def get_user_dao():
    return UserDao(model=User)


def get_location_dao():
    return LocationDao(model=Location)


def get_weather_service():
    return WeatherApiService()


def get_location_service():
    return LocationService()
