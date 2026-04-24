from sqlalchemy import Column, String, Numeric, Boolean, Date, ForeignKey
from .base import Base


class Payment(Base):
    __tablename__ = "payments"

    payment_id     = Column(String(20), primary_key=True)
    policy_id      = Column(String(20), ForeignKey("policies.policy_id"))
    payment_date   = Column(Date)
    amount_usd     = Column(Numeric(10, 2))
    payment_method = Column(String(30))
    status         = Column(String(20))
    is_late        = Column(Boolean)
    late_fee_usd   = Column(Numeric(8, 2))
