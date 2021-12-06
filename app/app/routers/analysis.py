from fastapi import BackgroundTasks, APIRouter, Depends, Request, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from ..jobs.algorithm import HazardWeights
from ..utils import auth, limiter
from ..database import database
from .jobs import DataPoint
import asyncpg

class Analysis(BaseModel):
    analysis: str
    public: bool
    id: asyncpg.pgproto.pgproto.UUID
    user_id: asyncpg.pgproto.pgproto.UUID

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
    responses={404: {"description": "Not found"}}
)

@router.get("/all", status_code=200, response_model=List[Analysis])
async def list_recordings(limit: int = 100, user=Depends(auth.get_current_user), db=Depends(database.provide_connection)):
    data = await db.fetch_all('SELECT * FROM analysis LIMIT :limit', values={"limit": limit})
    return data

@router.get("/list", status_code=200, response_model=List[Analysis])
async def list_recordings_by_user(limit: int = 100, user=Depends(auth.get_current_user), db=Depends(database.provide_connection)):
    data = await db.fetch_all('SELECT * FROM analysis WHERE user_id=:user_id LIMIT :limit', values={"user_id": user['id'], "limit": limit})
    return data