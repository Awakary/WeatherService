from typing import Any

from fastapi_cache import Coder
from starlette.responses import HTMLResponse


def image_path(weather) -> str:
    if weather == 'Ясно':
        return '/static/images/sun.png'
    elif 'нег' in weather:
        return '/static/images/snow.png'
    elif 'Облачно с прояснениями' in weather:
        return '/static/images/cloudy_sun.png'
    elif 'облач' in weather:
        return '/static/images/clouds.png'
    elif 'ождь' in weather:
        return '/static/images/rain2.png'
    else:
        return '/static/images/cloudy.png'


def image_number(number) -> str:
    match number:
        case 1:
            return '/static/images/city.png'
        case 2:
            return '/static/images/city_red.png'
        case 3:
            return '/static/images/city_green.png'
        case 4:
            return '/static/images/city_blue.png'
        case 5:
            return '/static/images/city_yellow.png'


class ORHTMLCoder(Coder):
    @classmethod
    def encode(cls, value: Any) -> bytes:
        return value.body

    @classmethod
    def decode(cls, value: bytes) -> Any:
        return HTMLResponse(value)


def custom_key_builder(*args, **kwargs) -> str:
    # Генерируем ключ на основе позиционных и именованных аргументов
    key = f"custom_key:{args}:{kwargs}"
    return key
