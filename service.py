from decimal import Decimal

from sqlalchemy import create_engine
from transliterate import translit
import requests

from config import settings
from exceptions import OpenWeatherApiException, NotCityException
from pd_models import LocationCheck, WeatherCheck, UserInDB

from sessions import LocationDao

location_dao = LocationDao()


class WeatherApiService:

    def __init__(self):
        self.api_key = "cdb8661536da243239d3811c4f088703"
        self.find_locations_url = "https://api.openweathermap.org/geo/1.0/direct"
        self.get_weather_url = "https://api.openweathermap.org/data/2.5/weather"

    def find_locations_by_name(self, city: str) -> list:
        if not city:
            raise NotCityException
        city = city[0].upper() + city[1:]
        found_locations = requests.get(self.find_locations_url,
                                       params={"q": city, "appid": self.api_key, "limit": 5, "lang": "ru"})
        if "cod" in found_locations and "message" in found_locations:
            raise OpenWeatherApiException
        deserialized_locations = found_locations.json()
        target_locations = self.filter_locations(deserialized_locations, city)
        return [LocationCheck(**location) for location in target_locations]

    @staticmethod
    def filter_locations(deserialized_locations: list, city: str) -> list:
        target_locations = []
        for location in deserialized_locations:
            if "local_names" in location:
                if any([city in value for value in location["local_names"].values()]):
                    if location["local_names"].get("ru", None):
                        location['name'] = location['local_names']["ru"]
                del location["local_names"]
            if city in location["name"] or translit(city[0], language_code='ru', reversed=True) in location["name"]:
                target_locations.append(location)
        return target_locations

    def get_weather_for_location(self, latitude: Decimal, longitude: Decimal) -> dict:
        weather = requests.get(self.get_weather_url,
                               params={"lat": latitude, "lon": longitude, "appid": self.api_key, "lang": "ru",
                                       "units": "metric"})
        if "cod" in weather and "message" in weather:
            raise OpenWeatherApiException
        return weather.json()

    def get_user_locations_with_weather(self, user: UserInDB) -> list:
        user_locations = location_dao.get_one(user)
        locations_with_weather = []
        for location in user_locations:
            weather_dict = self.get_weather_for_location(latitude=location.latitude,
                                                         longitude=location.longitude)
            weather_obj = WeatherCheck(main=weather_dict["weather"][0]["description"].capitalize(),
                                       temp=round(weather_dict["main"]["temp"], 0),
                                       feels_like=round(weather_dict["main"]["feels_like"], 0),
                                       wind_speed=weather_dict["wind"]["speed"],
                                       name=location.name,
                                       country=location.country,
                                       state=location.state,
                                       location_id=location.id)
            locations_with_weather.append(weather_obj)
        return locations_with_weather



