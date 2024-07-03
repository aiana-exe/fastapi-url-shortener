from fastapi import FastAPI, Depends, HTTPException
from db.db_setup import engine, get_db
from db.models import urlshortener
from db.models.urlshortener import UrlShortener
from sqlalchemy.orm import Session

from fastapi.responses import RedirectResponse
import hashlib
from urllib.parse import urlparse

urlshortener.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Utility functions

base_url = "http://short.url/"
#url_mapping = {}

def remove_protocol(url: str) -> str:
    after_removal_url = urlparse(url)
    return after_removal_url.netloc + after_removal_url.path

def shorten_url(db: Session, orig_url: str):
    after_removal_url = remove_protocol(orig_url)
    hash_value = hashlib.md5(after_removal_url.encode()).hexdigest()[:6]
    short_url = base_url + hash_value

    url_to_db = UrlShortener(
        original_url=orig_url,
        shortened_url=short_url,
    )
    db.add(url_to_db)
    db.commit()
    db.refresh(url_to_db)
    return url_to_db.shortened_url

    # list db logic
    # url_mapping[short_url] = after_removal_url
    # return short_url

def expand_url(db: Session, short_url: str):
    return db.query(UrlShortener).filter(UrlShortener.shortened_url == short_url).first().original_url
    # list db logic
    # original_url = url_mapping.get(short_url)
    # return original_url

def get_shortened_v_for_existing(db: Session, orig_url: str):
    orig_url=remove_protocol(orig_url)
    if db.query(UrlShortener).filter(UrlShortener.original_url == orig_url).first() is None:
        return None
    else: 
        return db.query(UrlShortener).filter(UrlShortener.original_url == orig_url).first().shortened_url

def get_all(db: Session):
    return db.query(UrlShortener).all()



# Endpoints

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/redirect")
async def redirecter(url_to_open: str):
    return RedirectResponse(url_to_open)

@app.post("/shorten")
async def shortener(orig_url: str, db: Session = Depends(get_db)):
    short_url = get_shortened_v_for_existing(db=db, orig_url=orig_url)
    if short_url:
        return short_url
    else: 
        return shorten_url(orig_url=orig_url, db=db)

@app.get("/expand")
async def expander(short_url: str, db: Session = Depends(get_db)):
    return expand_url(short_url=short_url, db=db)

@app.get("/all")
async def return_all(db: Session = Depends(get_db)):
    return get_all(db=db)
