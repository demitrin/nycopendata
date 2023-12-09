from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ARRAY, Numeric
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()
metadata = Base.metadata


class ClockTimeOptions(Base):
    __tablename__ = 'clock_time_options'

    id = Column(String, primary_key=True, default=str(uuid.uuid4()), nullable=False)
    raw_measure_column_value = Column(Numeric, nullable=False)
    # either something like 1.23 or 123. this is to be parsed by the frontend
    # and checked like "if value > 100, display value with colon. otherwise, decimal"
    measure_column_value_for_clock = Column(Numeric, nullable=False)
    # a number between 100 and 1260
    clock_time = Column(Numeric, nullable=False)
    measure_columns = Column(ARRAY(String), nullable=False)
    category_columns = Column(ARRAY(String), nullable=False)
    category_columns_values = Column(ARRAY(String), nullable=True)
    aggregate_function = Column(String, nullable=True)
    dataset = Column(String, nullable=False)
    units = Column(String, nullable=False)
    prompt = Column(String, nullable=True)
