from pydantic import BaseModel


class UrlShortener(BaseModel):
    id: int
    original_url: str
    shortened_url: str

    class Config:
        orm_mode = True
