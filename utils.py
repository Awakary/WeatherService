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

