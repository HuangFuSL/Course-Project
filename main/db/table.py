from sqlalchemy import DDL
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import event
from sqlalchemy import func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CommunityInfo(Base):
    __tablename__ = "community_info"

    community_name = Column(Text, primary_key=True)
    longtitude = Column(Float)
    latitude = Column(Float)
    area = Column(Text)
    street = Column(Text)

    fixed = relationship('fixed_info')

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}


class Volatile(Base):
    __tablename__ = "volatile_info"

    beike_ID = Column(Integer, ForeignKey('fixed_info.beike_ID'), primary_key=True)
    date = Column(DateTime, primary_key=True)
    title = Column(Text)
    price_per_square = Column(Integer)


class Fixed(Base):
    __tablename__ = "fixed_info"

    beike_ID = Column(Integer, primary_key=True)
    city = Column(Text)
    construct_time = Column(Integer)
    community_name = Column(Text, ForeignKey('community_info.community_name'))
    outer_square = Column(Float)
    inner_square = Column(Float)
    structure = Column(Integer)
    construction_type = Column(Integer)
    direction = Column(Integer)
    construction_struct = Column(Integer)
    decoration = Column(Integer)
    elevator_ratio = Column(Float)
    heating = Column(Integer)
    whether_elevator = Column(Boolean)
    listing_time = Column(DateTime)
    trade_property_right = Column(Integer)
    last_trade_time = Column(DateTime)
    house_usage = Column(Integer)
    property_right = Column(Integer)
    mortgage_info = Column(Integer)
    bedroom = Column(Integer)
    living_room = Column(Integer)
    bathroom = Column(Integer)
    floor_no = Column(Integer)

    volatile = relationship('volatile_info')

    __mapper_args__ = {"eager_defaults": True}


VOLATILE_FIELDS = ['beike_ID', 'date', 'title', 'price_per_square']
FIXED_FIELDS = [
    'beike_ID', 'city', 'construct_time', 'community_name', 'outer_square', 
    'inner_square', 'structure', 'construction_type', 'direction', 
    'construction_struct', 'decoration', 'elevator_ratio', 'heating',
    'whether_elevator', 'listing_time', 'trade_property_right',
    'last_trade_time', 'house_usage', 'property_right', 'mortgage_info', 
    'bedroom', 'living_room', 'bathroom', 'floor_no',
]
