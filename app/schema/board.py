from typing import Optional

from pydantic import BaseModel, Field


class BoardCreate(BaseModel):
    userid: str
    title: str
    contents: str

class NewReply(BaseModel):
    reply: str
    userid: str
    bno: int
    rpno: Optional[int] = Field(default=None)  # 선택사항