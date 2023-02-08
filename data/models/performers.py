from sqlalchemy import Column, Integer, BigInteger, String, DECIMAL, sql

from data.db_gino import BaseModel


class Performers(BaseModel):
    __tablename__ = "performers"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String)
    telephone = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String)
    performer_money = Column(DECIMAL(precision=8, asdecimal=True, scale=2), nullable=False, server_default="100")
    performer_rating = Column(DECIMAL(precision=8, asdecimal=True, scale=2), nullable=False, server_default="5")
    ban = Column(Integer, nullable=False, server_default="0")
    get_orders = Column(Integer, nullable=False, server_default="0")
    canceled_orders = Column(Integer, nullable=False, server_default="0")
    completed_orders = Column(Integer, nullable=False, server_default="0")
    performer_category = Column(String, nullable=False, server_default="pedestrian")
    performer_category_limit = Column(String)
    auto_send = Column(Integer, server_default="0")
    money_added = Column(BigInteger, nullable=False, server_default="0")
    money_earned = Column(BigInteger, nullable=False, server_default="0")

    query: sql.select


class PerformerPersonalData(BaseModel):
    __tablename__ = "performers_personal_data"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False, unique=True)
    telephone = Column(String, nullable=False)
    real_first_name = Column(String, nullable=False)
    real_last_name = Column(String, nullable=False)
    selfie = Column(String, nullable=False)

    query: sql.select


class AutoSendJobOffer(BaseModel):
    __tablename__ = "auto_send_job_offer"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=False, unique=True)
    start = Column(String, nullable=False)
    end = Column(String, nullable=False)

    query: sql.select
