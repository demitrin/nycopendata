from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ARRAY, create_engine
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()
metadata = Base.metadata


class ClockTimeOptions(Base):
    __tablename__ = 'clock_time_options'

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    clock_time = Column(Integer, nullable=False)
    measure_columns = Column(ARRAY(String))
    category_columns = Column(ARRAY(String))
    dataset = Column(String)