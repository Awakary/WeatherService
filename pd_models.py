import re
from decimal import Decimal
from typing import List

import pydantic
from pydantic import BaseModel, ConfigDict, root_validator, validator, model_validator, ValidationError, constr

from exceptions import UsernamePasswordException


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

    # @model_validator(mode='after')
    # def validate_all_fields(self):
    #     if (not re.match(latin_regex, self.login) or not re.match(latin_regex, self.password)
    #             or not re.match(latin_regex, self.repeated_password)):
    #         raise UsernamePasswordException
    #     return self





class LocationCheck(BaseModel):
    name: str
    lat: Decimal
    lon: Decimal
    country: str
    state: str = None


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
    wind_speed: float
    country: str
    state: str = "-"




