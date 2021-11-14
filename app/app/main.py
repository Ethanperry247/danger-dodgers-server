from .routers import reports, users
from .database import database

from typing import Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel

from .utils import limiter

app = FastAPI()
limiter.attach_limiter(app)

app.include_router(users.router)
app.include_router(reports.router)

@app.on_event("startup")
async def start():
    await database.startup()

@app.on_event("shutdown")
async def stop():
    await database.shutdown()

@app.get("/", status_code=200)
async def root(request: Request):
    # await authenticate_user("ethanperry247@gmail.com", "pass")
    return {"Hello": "World"}

