from sqlalchemy import Column, Integer, BigInteger, String, DECIMAL, sql
from sqlalchemy.dialects.postgresql import TIMESTAMP

from data.db_gino import BaseModel


class Admins(BaseModel):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    query: sql.select


class Payment(BaseModel):
    __tablename__ = "payment"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    money = Column(DECIMAL, nullable=False)
    bill_id = Column(String, nullable=False, unique=True)
    query: sql.select


class PrivateChat(BaseModel):
    __tablename__ = "private_chat"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False, unique=True)
    count_word = Column(Integer, server_default="0")
    enter_date = Column(TIMESTAMP(timezone=False), nullable=False)
    query: sql.select


class Limitations(BaseModel):
    __tablename__ = "limitations"
    id = Column(Integer, primary_key=True, nullable=False)
    value = Column(String)
    limit = Column(Integer)
    query: sql.select
