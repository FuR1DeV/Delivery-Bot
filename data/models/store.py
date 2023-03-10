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

    query: sql.select
