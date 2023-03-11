from sqlalchemy import Column, Integer, BigInteger, String, DECIMAL, sql

from data.db_gino import BaseModel


class Store(BaseModel):
    __tablename__ = "store"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String)
    telephone = Column(String, nullable=False)
    store_name = Column(String, nullable=False)
    rating = Column(String, server_default='5')
    created_orders = Column(Integer, nullable=False, server_default="0")
    canceled_orders = Column(Integer, nullable=False, server_default="0")
    completed_orders = Column(Integer, nullable=False, server_default="0")

    query: sql.select


class StoreOrders(BaseModel):
    __tablename__ = "store_orders"
    id = Column(Integer, primary_key=True, nullable=False)
    client_id = Column(BigInteger, nullable=False, unique=True)
    geo_position_to = Column(String)
    price = Column(DECIMAL, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String)
    video = Column(String)
    video_note = Column(String)
    voice = Column(String)
    in_work = Column(BigInteger, server_default="0")
    completed = Column(Integer, server_default="0")
    order_id = Column(String, nullable=False)
    order_create = Column(String, nullable=False)
    order_get = Column(String)
    block = Column(Integer, server_default="0")
    order_expired = Column(String)
    order_worth = Column(Integer, server_default="0")
    order_rating = Column(Integer, server_default="0")

    query: sql.select

