from sqlalchemy import Column, String, Integer, Date
from .base import Base


class Policyholder(Base):
    __tablename__ = "policyholders"

    policyholder_id    = Column(String(20), primary_key=True)
    full_name          = Column(String(100), nullable=False)
    date_of_birth      = Column(Date)
    age                = Column(Integer)
    gender             = Column(String(10))
    state              = Column(String(5))
    phone              = Column(String(15))
    email              = Column(String(100))
    license_years      = Column(Integer)
    prior_claims_count = Column(Integer)
    credit_score       = Column(Integer)
    marital_status     = Column(String(20))
