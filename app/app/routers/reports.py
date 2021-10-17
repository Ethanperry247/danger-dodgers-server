from enum import Enum

from fastapi import FastAPI
from fastapi import APIRouter

class Hazard(str, Enum):
        Water = "Water"
        Ice = "Ice"
        Potholes = "Potholes"
        BadRoadConditions = "Bad Road Conditions"
        TightTurn = "Tight Turn"
        Debris = "Debris"

router = APIRouter(
        prefix="/report",
        tags=["report"],
        responses={404: {"description": "Not found"}},
)