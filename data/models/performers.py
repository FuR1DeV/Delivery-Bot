from sqlalchemy import Column, Integer, BigInteger, String, DECIMAL, sql
from sqlalchemy.dialects.postgresql import TIMESTAMP

from data.db_gino import BaseModel


class Performers(BaseModel):
    __tablename__ = "performers"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String)
    telephone = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    performer_money = Column(DECIMAL(precision=8, asdecimal=True, scale=2), nullable=False, server_default="0")
    performer_rating = Column(DECIMAL(precision=8, asdecimal=True, scale=2), nullable=False, server_default="5")
    ban = Column(Integer, nullable=False, server_default="0")
    get_orders = Column(Integer, nullable=False, server_default="0")
    canceled_orders = Column(Integer, nullable=False, server_default="0")
    performer_category = Column(String, nullable=False, server_default="pedestrian")
    performer_category_limit = Column(String)

    query: sql.select
