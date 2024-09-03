from pydantic import BaseModel

class NewMusic(BaseModel):
    title: str
    singer: str
    year: int
    genre: str
    country :str
    ment: str
    lyrics: str
    iname: str
    fname: str

class NewMusicVideo(BaseModel):
    lyrics: str
    iname: str
    fname: str

class NewStorage(BaseModel):
    userid: str
    mno: int