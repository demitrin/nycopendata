from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ARRAY, Numeric
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()
metadata = Base.metadata


class ClockTimeOptions(Base):
    __tablename__ = 'clock_time_options'

    id = Column(String, primary_key=True, default=str(uuid.uuid4()), nullable=False)
    clock_time = Column(Integer, nullable=False)
    measure_column_value = Column(Numeric, nullable=False)
    measure_columns = Column(ARRAY(String), nullable=False)
    category_columns = Column(ARRAY(String), nullable=False)
    category_columns_values = Column(ARRAY(String), nullable=True)
    aggregate_function = Column(String, nullable=True)
    dataset = Column(String, nullable=False)