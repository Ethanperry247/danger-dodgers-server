from enum import Enum

from pydantic import BaseModel
from ..database import database
from ..utils import auth

from fastapi import APIRouter, Depends

class Hazard(str, Enum):
        Water = "Water"
        Ice = "Ice"
        Potholes = "Potholes"
        BadRoadConditions = "Bad Road Conditions"
        TightTurn = "Tight Turn"
        Debris = "Debris"

class Report(BaseModel):
        pass

router = APIRouter(
        prefix="/report",
        tags=["report"],
        responses={404: {"description": "Not found"}}
)

@router.get("/list", status_code=200)
async def list_reports(user = Depends(auth.get_current_user)):
    return "Not yet implemented!"

@router.get("/{id}", status_code=200)
async def get_report(user = Depends(auth.get_current_user)):
    return "Not yet implemented!"

@router.post("/{id}", status_code=200)
async def create_report(user = Depends(auth.get_current_user)):
    return "Not yet implemented!"

@router.patch("/{id}", status_code=200)
async def update_report(user = Depends(auth.get_current_user)):
    return "Not yet implemented!"

@router.delete("/{id}", status_code=200)
async def delete_report(user = Depends(auth.get_current_user)):
    return "Not yet implemented!"

@router.post("/upvote/{id}", status_code=200)
async def upvote_report(user = Depends(auth.get_current_user)):
    return "Not yet implemented!"

@router.post("/downvote/{id}", status_code=200)
async def downvote_report(user = Depends(auth.get_current_user)):
    return "Not yet implemented!"