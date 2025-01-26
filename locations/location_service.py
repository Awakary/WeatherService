from users.authorization import passwords as user_funcs
from users.schemas import LocationCheckUser


class LocationService:

    def __init__(self):
        self.result_dict = {'paginated_user_locations': [],
                            'total_pages': 0}

    def get_result_locations(self, page: int, token: str, user_dao, loc_dao,
                             weather_service, current_page) -> dict:
        if token:
            current_user = user_funcs.get_current_user(token, user_dao)
            user_locations = loc_dao.get_all(current_user)
            saved_locations = weather_service.get_user_locations_with_weather(user_locations=user_locations)
            self.calc_paginated_locations_and_total_pages(saved_locations, page)
        self.result_dict["current_page"] = current_page if current_page else page
        return self.result_dict

    def calc_paginated_locations_and_total_pages(self, saved_locations: list, page: int) -> None:
        total_pages = len(saved_locations) // 5 + 1 if len(saved_locations) % 5 != 0 else len(saved_locations) // 5
        page = page - 1 if page > total_pages else page
        paginated_user_locations = saved_locations[page * 5 - 5: page * 5] if page != 1 else saved_locations[0:5]
        self.result_dict['paginated_user_locations'] = paginated_user_locations
        self.result_dict['total_pages'] = total_pages

    @staticmethod
    def get_location_db(data, current_user):
        location_dict = data.model_dump()
        lon, lat = location_dict.pop("lon"), location_dict.pop("lat")
        location_for_db = LocationCheckUser(**location_dict, user_id=current_user.id,
                                            latitude=lat, longitude=lon)
        return location_for_db
