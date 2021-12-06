from fastapi import BackgroundTasks, APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional, List
from ..jobs.algorithm import HazardWeights
from ..utils import auth, limiter
from ..database import database


class DataPoint(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    time: int

class Recording(BaseModel):
    recording: List[dict]
    public: bool


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    responses={404: {"description": "Not found"}}
)

limit = limiter.provide_limiter()

async def analyze_recording(recording: Recording, db, user_id):
    analysis = HazardWeights(py=recording.recording)
    async with db.transaction():
        await db.execute("INSERT INTO analysis (analysis, user_id, public) VALUES (:analysis, :user_id, :public)", values={"analysis": str(analysis.to_response_format()), "user_id": user_id['id'], "public": recording.public })

@router.post("/recording", status_code=202)
@limit.limit("2/minute")
async def process_recording(request: Request,recording: Recording, background_tasks: BackgroundTasks, user=Depends(auth.get_current_user), db=Depends(database.provide_connection)):
    background_tasks.add_task(
        analyze_recording, recording=recording, db=db, user_id=user)
    return {"message": "Recording being processed in the background"}
