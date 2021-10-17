from enum import Enum

from fastapi import FastAPI
from fastapi import APIRouter

class ModelName(str, Enum):
        something = ""

router = APIRouter(
        prefix="/report",
        tags=["report"],
        responses={404: {"description": "Not found"}},
)