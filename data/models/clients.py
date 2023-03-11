from sqlalchemy import Column, Integer, BigInteger, String, DECIMAL, sql

from data.db_gino import BaseModel


class Client(BaseModel):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String)
    telephone = Column(String, nullable=False)
    created_orders = Column(Integer, nullable=False, server_default="0")
    canceled_orders = Column(Integer, nullable=False, server_default="0")
    completed_orders = Column(Integer, nullable=False, server_default="0")

    query: sql.select
