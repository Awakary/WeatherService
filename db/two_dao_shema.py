from pydantic import BaseModel

from db.sessions import UserDao, LocationDao


class TwoDaoHelper(BaseModel):
    user: UserDao
    location: LocationDao

    class Config:
        arbitrary_types_allowed = True
