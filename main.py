from fastapi import FastAPI, Depends, HTTPException
# from db.db_setup import engine, get_db
from db.models import urlshortener
from db.models.urlshortener import UrlShortener
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import IntegrityError

from fastapi.responses import RedirectResponse
import hashlib
from urllib.parse import urlparse

from pkg.redis_tools.tools import RedisTools


app = FastAPI()


# Utility functions

base_url = "http://short.url/"
#url_mapping = {}

def remove_protocol(url: str) -> str:
    after_removal_url = urlparse(url)
    return after_removal_url.netloc + after_removal_url.path

def find_url_by_orig(orig_url: str):
    url=remove_protocol(orig_url)
    
    if url not in [s.decode('utf-8') for s in RedisTools.get_keys()]:
        return None
    else:
        return {
            'original_url': url,
            'shortened_url': RedisTools.get_value(url)
        }


def find_url_by_short(short_url: str):
    key_val_dict=RedisTools.get_keys_and_values()
    
    for key, value in key_val_dict.items():
        if short_url == value:
            return key
    
    return None
    

def shorten_url(orig_url: str):
    after_removal_url = remove_protocol(orig_url)
    hash_value = hashlib.md5(after_removal_url.encode()).hexdigest()[:6]
    short_url = base_url + hash_value
    
    RedisTools.set_pair(after_removal_url, short_url)

    return RedisTools.get_value(after_removal_url)

def get_all():
    return RedisTools.get_keys_and_values()



# Endpoints


@app.post("/shorten")
async def shortener(orig_url: str):
    short_url_obj = find_url_by_orig(orig_url=orig_url)
    if short_url_obj is None:
        return shorten_url(orig_url=orig_url)
    else: 
        return short_url_obj.shortened_url

@app.get("/expand")
async def expander(short_url: str):
    orig_url = find_url_by_short(short_url=short_url)
    if orig_url is None:
        return "Invalid short URL."
    else:
        return orig_url

@app.get("/all")
async def return_all():
    return get_all()


@app.get("/{short_hash}")
async def redirecter(short_hash: str):

    short_url = base_url + short_hash
    orig_url = find_url_by_short(short_url=short_url)
    if orig_url is None:
        raise HTTPException(status_code=404, detail="Invalid short URL.")
    else:
        return RedirectResponse(orig_url)
    
    
