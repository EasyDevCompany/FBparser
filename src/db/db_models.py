import uuid

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from .db import Base


class MarketItem(Base):
    __tablename__ = "market_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    header = Column(String, unique=True, nullable=False)
    image = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    property_type = Column(String, nullable=False)
    info = Column(String, nullable=False)
    area = Column(String, nullable=True)
    coordinates = Column(String, nullable=True)
    description = Column(String, nullable=False)
    owner_link = Column(String, nullable=False)

    def __init__(self, header, price, property_type, info, area, coordinates, description, owner_link):
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
