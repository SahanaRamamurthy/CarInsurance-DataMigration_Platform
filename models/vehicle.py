from sqlalchemy import Column, String, Integer, Numeric, Boolean, ForeignKey
from .base import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id        = Column(String(20), primary_key=True)
    policyholder_id   = Column(String(20), ForeignKey("policyholders.policyholder_id"))
    make              = Column(String(50))
    model             = Column(String(50))
    year              = Column(Integer)
    color             = Column(String(30))
    vehicle_value_usd = Column(Numeric(12, 2))
    mileage           = Column(Integer)
    fuel_type         = Column(String(20))
    vin               = Column(String(30))
    is_modified       = Column(Boolean)
