from sqlalchemy import Column, Integer, BigInteger, String, DECIMAL, sql

from data.db_gino import BaseModel


class Customers(BaseModel):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String)
    telephone = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    customer_money = Column(DECIMAL(precision=8, asdecimal=True, scale=2), nullable=False, server_default="0")
    customer_rating = Column(DECIMAL(precision=8, asdecimal=True, scale=2), nullable=False, server_default="5.0")
    ban = Column(Integer, nullable=False, server_default="0")
    create_orders = Column(Integer, nullable=False, server_default="0")
    canceled_orders = Column(Integer, nullable=False, server_default="0")

    query: sql.select
