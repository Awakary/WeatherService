from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class UserCheck(BaseModel):
    login: str

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserCheck):
    hashed_password: str
    id: int


class TokenCheck(BaseModel):
    access_token: str
    token_type: str


class FormData(BaseModel):
    login: str
    password: str


class FormDataCreate(FormData):
    repeated_password: str


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
