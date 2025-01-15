from jinja2 import Environment, FileSystemLoader


def image_path(weather):
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


def image_number(number):
    if number == 1:
        return '/static/images/city.png'
    elif number == 2:
        return '/static/images/city_red.png'
    elif number == 3:
        return '/static/images/city_green.png'
    elif number == 4:
        return '/static/images/city_blue.png'
    elif number == 5:
        return '/static/images/city_yellow.png'


def get_paginated_locations_and_total_pages(user_locations: list, page: int) -> tuple:
    total_pages = len(user_locations) // 5 + 1 if len(user_locations) % 5 != 0 else len(user_locations) // 5
    page = page - 1 if page > total_pages else page
    paginated_user_locations = user_locations[page * 5 - 5: page * 5] if page != 1 else user_locations[0:5]
    return paginated_user_locations, total_pages
