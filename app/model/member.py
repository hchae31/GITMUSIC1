from datetime import datetime
from sqlalchemy.orm import mapped_column, Mapped
from app.model.base import Base
from sqlalchemy.orm import relationship


class Member(Base):
    __tablename__ = 'member'

    mno: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    userid: Mapped[str] = mapped_column(index=True, unique=True)
    passwd: Mapped[str]
    name: Mapped[str]
    email: Mapped[str]
    regdate: Mapped[datetime] = mapped_column(default=datetime.now)
    storage_items = relationship("Storage", backref="member")
    payment = relationship("Payment", back_populates="member", uselist=False)

