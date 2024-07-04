from fastapi import FastAPI, Depends, HTTPException
from db.db_setup import engine, get_db
from db.models import urlshortener
from db.models.urlshortener import UrlShortener
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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

def find_url_by_orig(db: Session, orig_url: str):
    url=remove_protocol(orig_url)
    return db.query(UrlShortener).filter(UrlShortener.original_url == orig_url).first()


def find_url_by_short(db: Session, short_url: str):
    return db.query(UrlShortener).filter(UrlShortener.shortened_url == short_url).first()

def shorten_url(db: Session, orig_url: str):
    after_removal_url = remove_protocol(orig_url)
    hash_value = hashlib.md5(after_removal_url.encode()).hexdigest()[:6]
    short_url = base_url + hash_value

    url_to_db = UrlShortener(
        original_url=after_removal_url,
        shortened_url=short_url,
    )
    db.add(url_to_db)
    db.commit()
    db.refresh(url_to_db)

    return url_to_db.shortened_url

def get_all(db: Session):
    return db.query(UrlShortener).all()



# Endpoints


@app.post("/shorten")
async def shortener(orig_url: str, db: Session = Depends(get_db)):
    short_url_obj = find_url_by_orig(db=db, orig_url=orig_url)
    if short_url_obj is None:
        return shorten_url(orig_url=orig_url, db=db)
    else: 
        return short_url_obj.shortened_url

@app.get("/expand")
async def expander(short_url: str, db: Session = Depends(get_db)):
    orig_url_obj = find_url_by_short(db=db, short_url=short_url)
    if orig_url_obj is None:
        return "Invalid short URL."
    else:
        return orig_url_obj.original_url

@app.get("/all")
async def return_all(db: Session = Depends(get_db)):
    return get_all(db=db)


@app.get("/{short_hash}")
async def redirecter(short_hash: str, db: Session = Depends(get_db)):

    short_url = base_url + short_hash
    orig_url_obj = find_url_by_short(db=db, short_url=short_url)
    if orig_url_obj is None:
        raise HTTPException(status_code=404, detail="Invalid short URL.")
    else:
        return RedirectResponse(orig_url_obj.original_url)
