from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class LocationCheck(BaseModel):
    name: str
    lat: Decimal
    lon: Decimal
    country: str
    state: str = "-"


class LocationCheckUser(BaseModel):
    user_id: int
    name: str
    latitude: Decimal
    longitude: Decimal
    country: str
    state: str = "-"


class WeatherCheck(BaseModel):
    location_id: int
    name: str
    main: str
    temp: int
    feels_like: int
    wind_speed: int
    country: str
    state: str = '-'
