from sqlalchemy import Column, String, Numeric, Boolean, Date, ForeignKey
from .base import Base


class Policy(Base):
    __tablename__ = "policies"

    policy_id           = Column(String(20), primary_key=True)
    policyholder_id     = Column(String(20), ForeignKey("policyholders.policyholder_id"))
    vehicle_id          = Column(String(20), ForeignKey("vehicles.vehicle_id"))
    coverage_type       = Column(String(50))
    start_date          = Column(Date)
    end_date            = Column(Date)
    premium_usd         = Column(Numeric(10, 2))
    deductible_usd      = Column(Numeric(10, 2))
    is_active           = Column(Boolean)
    agent_id            = Column(String(20))
    coverage_amount_usd = Column(Numeric(12, 2))
