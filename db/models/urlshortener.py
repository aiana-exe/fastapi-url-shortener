from sqlalchemy import Column, Integer, String

from ..db_setup import Base



class UrlShortener(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String(200), nullable=False)
    shortened_url = Column(String(200), nullable=False)