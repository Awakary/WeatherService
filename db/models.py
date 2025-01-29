from decimal import Decimal
from typing import Annotated

from sqlalchemy import ForeignKey, create_engine, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import settings

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

engine = create_engine(
    url=settings.DB_URL,
    echo=False
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'

    id: Mapped[intpk]
    login: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)


class Location(Base):
    __tablename__ = 'location'

    id: Mapped[intpk]
    name: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    latitude: Mapped[Decimal]
    longitude: Mapped[Decimal]
    country: Mapped[str]
    state: Mapped[str]

    __table_args__ = (
        UniqueConstraint('name', 'latitude', 'longitude', 'user_id', name='name_user_uc'),
    )


Base.metadata.create_all(engine)
