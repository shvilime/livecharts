from typing import Optional
from datetime import datetime
from pydantic import BaseConfig, BaseModel, Field
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

from application.routes import DATE_FORMAT

AlchemyBase = declarative_base()


class QuoteScheme(AlchemyBase):
    class Config(BaseConfig):
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        orm_mode = True

    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created = Column(DateTime, nullable=False)
    ticker = Column(String(20), nullable=False)
    movement = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)


class Quote(BaseModel):
    class Config(BaseConfig):
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        orm_mode = True

    created: Optional[datetime] = Field(default_factory=datetime.now)
    ticker: str
    price: int = Field(alias="value")


class Quotes(BaseModel):
    class Config(BaseConfig):
        json_encoders = {
            datetime: lambda v: datetime.strftime(v, DATE_FORMAT),
        }
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        orm_mode = True

    start_live: Optional[bool] = Field(default=False)
    values: Optional[list] = Field(default=[])
