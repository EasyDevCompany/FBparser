import uuid

from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .db import Base


class MarketItem(Base):
    __tablename__ = "market_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    item_link = Column(String, unique=True, nullable=False)  # ссылка на объект
    header = Column(String, nullable=False)  # заголовок
    image = Column(String, nullable=True)  # изображение
    price = Column(Integer, nullable=False)  # цена
    property_type = Column(String, nullable=True)  # тип недвижимости
    info = Column(String, nullable=True)  # информация о недвижимости
    area = Column(String, nullable=True)  # квадратура
    coordinates = Column(String, nullable=True)  # координаты
    description = Column(String, nullable=False)  # описание
    owner_link = Column(String, nullable=False)  # ссылка на владельца
    created_at = Column(Date, server_default=func.now())  # дата создания записи в бд

    def __init__(self, item_link, header, price, property_type, info, area, coordinates, description, owner_link):
        self.item_link = item_link
        self.header = header
        self.price = price
        self.property_type = property_type
        self.info = info
        self.area = area
        self.coordinates = coordinates
        self.description = description
        self.owner_link = owner_link

    def __repr__(self):
        return f"<{self.header}>"
