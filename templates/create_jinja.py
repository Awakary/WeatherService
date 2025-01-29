from starlette.templating import Jinja2Templates

from utilites.utils import image_path, image_number

templates = Jinja2Templates(directory='templates')

# Регистрация фильтров
templates.env.filters['image_path'] = image_path
templates.env.filters['image_number'] = image_number
