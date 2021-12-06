from .routers import reports, users, jobs, analysis
from .database import database

from typing import Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .utils import limiter

# Dotenv for secrets and environment configuration. 
from dotenv import load_dotenv

# Loads key value pairs from the environment.
load_dotenv()

app = FastAPI()
limiter.attach_limiter(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(reports.router)
app.include_router(jobs.router)
app.include_router(analysis.router)

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

# Used for debugging.
@app.post("/", status_code=200)
async def root(request: Request):
    print(request.headers)
    # await authenticate_user("ethanperry247@gmail.com", "pass")
    print(await request.json())
    return {"Hello": "World"}

@app.get("/header", status_code=200)
async def root(request: Request):
    print(request.headers)
    # await authenticate_user("ethanperry247@gmail.com", "pass")
    # print(await request.json())
    return {"Hello": "World"}

