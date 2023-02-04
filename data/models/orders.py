from sqlalchemy import Column, Integer, BigInteger, String, DECIMAL, sql, Text, ARRAY

from data.db_gino import BaseModel


class Orders(BaseModel):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    geo_position_from = Column(String, nullable=False)
    geo_position_to = Column(String, nullable=False)
    title = Column(String, nullable=False)
    price = Column(DECIMAL, nullable=False)
    description = Column(String, nullable=False)
    image = Column(String)
    video = Column(String)
    in_work = Column(BigInteger, server_default="0")
    completed = Column(Integer, server_default="0")
    order_id = Column(String, nullable=False)
    order_create = Column(String, nullable=False)
    order_get = Column(String)
    order_end = Column(String)
    category_delivery = Column(String, nullable=False)
    block = Column(Integer, server_default="0")
    performer_category = Column(String, nullable=False)
    order_expired = Column(String)
    order_worth = Column(Integer, server_default="0")
    order_rating = Column(Integer, server_default="0")
    query: sql.select


class OrdersLoading(BaseModel):
    __tablename__ = "orders_loading"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    geo_position = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(DECIMAL, nullable=False)
    start_time = Column(String, nullable=False)
    image = Column(String)
    video = Column(String)
    in_work = Column(BigInteger, server_default="0")
    completed = Column(Integer, server_default="0")
    order_id = Column(String, nullable=False)
    order_create = Column(String, nullable=False)
    order_get = Column(String)
    order_end = Column(String)
    order_expired = Column(String)
    order_rating = Column(Integer, server_default="0")
    person = Column(Integer, nullable=False)
    count_person = Column(Integer, server_default="0")
    block = Column(Integer, server_default="0")
    persons_list = Column(ARRAY(BigInteger))
    query: sql.select


class OrdersStatus(BaseModel):
    __tablename__ = "orders_status"
    id = Column(Integer, primary_key=True, nullable=False)
    performer_status = Column(Integer, server_default="0")
    customer_status = Column(Integer, server_default="0")
    order_id = Column(String, nullable=False)
    performer_arrive = Column(String, server_default="3")
    customer_arrive = Column(String, server_default="3")
    query: sql.select


class Commission(BaseModel):
    __tablename__ = "commission"
    id = Column(Integer, primary_key=True, nullable=False)
    category = Column(String)
    commission = Column(DECIMAL(precision=8, asdecimal=True, scale=2))
    query: sql.select


class Reviews(BaseModel):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, nullable=False)
    review_from_customer = Column(Text)
    review_from_performer = Column(Text)
    rating_from_customer = Column(Integer)
    rating_from_performer = Column(Integer)
    order_id = Column(String, nullable=False)
    query: sql.select


class CommissionPromo(BaseModel):
    __tablename__ = "commission_promo"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    percent = Column(DECIMAL(precision=8, asdecimal=True, scale=2), server_default="0.0")
    promo_time = Column(String, nullable=False)
    query: sql.select


class OrdersRating(BaseModel):
    __tablename__ = "orders_rating"
    id = Column(Integer, primary_key=True, nullable=False)
    order_id = Column(String, nullable=False)
    rating = Column(Integer, server_default="0")
    user_id = Column(BigInteger, nullable=False)
    query: sql.select
