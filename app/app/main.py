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

@app.get("/hazards/", status_code=200)
async def list_hazards():
    return "Not yet implemented!"

@app.get("/hazard/{id}", status_code=200)
async def get_hazard():
    return "Not yet implemented!"

@app.post("/hazard/{id}", status_code=200)
async def create_hazard():
    return "Not yet implemented!"

@app.patch("/hazard/{id}", status_code=200)
async def update_hazard():
    return "Not yet implemented!"

@app.delete("/hazard/{id}", status_code=200)
async def delete_hazard():
    return "Not yet implemented!"

