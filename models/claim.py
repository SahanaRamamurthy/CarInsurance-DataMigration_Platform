from sqlalchemy import Column, String, Integer, Numeric, Boolean, Date, Text, ForeignKey
from .base import Base


class Claim(Base):
    __tablename__ = "claims"

    claim_id           = Column(String(20), primary_key=True)
    policy_id          = Column(String(20), ForeignKey("policies.policy_id"))
    claim_date         = Column(Date)
    claim_type         = Column(String(50))
    claim_amount_usd   = Column(Numeric(12, 2))
    settled_amount_usd = Column(Numeric(12, 2))
    status             = Column(String(30))
    description        = Column(Text)
    is_fraud_flag      = Column(Boolean)
    days_to_report     = Column(Integer)
