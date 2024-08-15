from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException

from crawl import Crawler
from data_access import DataAccess

app = FastAPI()
data_access = DataAccess()
crawler = Crawler()


@app.get("/isalive")
async def is_alive():
    return {"isAlive": True}


@app.get("/screenshots/{item_id}")
async def get_screenshots_by_id(item_id: str):
    return {item_id: data_access.get_files_by_id(item_id)}


@app.post("/screenshots")
async def post_screenshots(start_url: str, max_links: int):
    parsed_url = urlparse(start_url)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise HTTPException(status_code=400, detail="Invalid start_url parameter.")
    if max_links <= 0:
        raise HTTPException(status_code=400, detail="Max links must be a positive number.")
    crawl_id: str = crawler.crawl(start_url=start_url, max_links=max_links)
    return {"id": crawl_id}
