from datetime import datetime, timedelta

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.model.base import Base


class Payment(Base):
    __tablename__ = 'payment'

    pno: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    userid: Mapped[str] = mapped_column(ForeignKey('member.userid'))
    payment_date: Mapped[datetime] = mapped_column(default=datetime.now)
    reg_date: Mapped[datetime] = mapped_column(default=lambda: datetime.now() + timedelta(days=31))
    member = relationship("Member", back_populates="payment")

    def __repr__(self):
        return f"<Payment(pno={self.pno}, userid='{self.userid}', payment_date={self.payment_date}, reg_date={self.reg_date})>"