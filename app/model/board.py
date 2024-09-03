from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.model.base import Base


# 게시판 테이블
class Board(Base):
    __tablename__ = 'board'

    bno: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    title: Mapped[str] = mapped_column(index=True)
    userid: Mapped[str] = mapped_column(ForeignKey('member.userid')) # Member의 userid
    regdate: Mapped[datetime] = mapped_column(default=datetime.now)
    views: Mapped[int] = mapped_column(default=0)
    contents: Mapped[str]
    replys = relationship('Reply', back_populates='board')
    files = relationship("BoardFile", back_populates="board", cascade="all, delete-orphan")

# 게시판 파일업로드 테이블
class BoardFile(Base):
    __tablename__ = 'boardfile'
    fno: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    bno: Mapped[int] = mapped_column(ForeignKey('board.bno'), index=True)
    fname: Mapped[str] = mapped_column(nullable=False)
    fsize: Mapped[int] = mapped_column(default=0)
    regdate: Mapped[datetime] = mapped_column(default=datetime.now)
    board = relationship("Board", back_populates="files")

# 게시판 댓글
class Reply(Base):
    __tablename__ = 'reply'

    rno: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    reply: Mapped[str] = mapped_column(index=True)
    userid: Mapped[str] = mapped_column(ForeignKey('member.userid'), index=True)
    regdate: Mapped[datetime] = mapped_column(default=lambda: datetime.now().replace(microsecond=0))
    bno: Mapped[int] = mapped_column(ForeignKey('board.bno'))
    rpno: Mapped[int] = mapped_column(ForeignKey('reply.rno'))
    board = relationship('Board', back_populates='replys')
