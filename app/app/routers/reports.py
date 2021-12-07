from enum import Enum
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel
from ..database import database
from ..utils import auth, limiter

from fastapi import APIRouter, Depends, Request, HTTPException, status
import asyncpg

import math


class Hazard(str, Enum):
    Water = "Water"
    Ice = "Ice"
    Potholes = "Potholes"
    BadRoadConditions = "Bad Road Conditions"
    TightTurn = "Tight Turn"
    Debris = "Debris"

class Frequency(BaseModel):
    frequency: str

class Report(BaseModel):
    type: Optional[Hazard] = None
    risk_level: Optional[int] = None
    description: Optional[str] = None
    title: Optional[str] = None
    id: Optional[str] = None
    timestamp: Optional[datetime] = None
    latitude: float
    longitude: float


class PatchReport(BaseModel):
    type: Optional[Hazard] = None
    risk_level: Optional[int] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    title: Optional[str] = None


class FullReport(Report):
    # UUID class used by asyncPG.
    # Will resolve to string before sending to client.
    id: asyncpg.pgproto.pgproto.UUID
    user_id: asyncpg.pgproto.pgproto.UUID
    frequency: int


limit = limiter.provide_limiter()

router = APIRouter(
    prefix="/report",
    tags=["report"],
    responses={404: {"description": "Not found"}}
)

R = 6371 * (10 ** 3)

@router.get("/filter/lat/{lat}/long/{long}/", status_code=200, response_model=List[FullReport])
async def filter_reports(lat: float, long: float, radius: float = 1000.0, limit: int = 100, user=Depends(auth.get_current_user), db=Depends(database.provide_connection)):

    minimumLat = lat - radius / R * 180 / math.pi
    maxmimumLat = lat + radius / R * 180 / math.pi
    minimumLong = long - radius / R * 180 / math.pi / math.cos(lat * math.pi / 180)
    maximumLong = long + radius / R * 180 / math.pi / math.cos(lat * math.pi / 180)

    # For efficiency sake, do not find the closest points if the desired radius is over 15km.
    if (radius < 15000):
        return await db.fetch_all("SELECT * FROM report WHERE latitude BETWEEN :minimumLat AND :maxmimumLat AND longitude BETWEEN :minimumLong AND :maximumLong ORDER BY (SQRT(POWER(:latitude - latitude, 2) + POWER(:longitude - longitude, 2))) LIMIT :limit", values={ "minimumLat": minimumLat, "maxmimumLat": maxmimumLat, "minimumLong": minimumLong, "maximumLong": maximumLong, "latitude": lat, "longitude": long, "limit": limit})
    else:
        return await db.fetch_all("SELECT * FROM report WHERE latitude BETWEEN :minimumLat AND :maxmimumLat AND longitude BETWEEN :minimumLong AND :maximumLong LIMIT :limit", values={ "minimumLat": minimumLat, "maxmimumLat": maxmimumLat, "minimumLong": minimumLong, "maximumLong": maximumLong, "limit": limit})


@router.get("/list", status_code=200, response_model=List[FullReport])
async def list_reports_by_user_id(limit: int = 100, user=Depends(auth.get_current_user), db=Depends(database.provide_connection)):
    res = await db.fetch_all("SELECT * FROM report WHERE user_id=:id ORDER BY timestamp DESC", values={"id": str(dict(user)['id'])})
    return res


@router.get("/{id}", status_code=200, response_model=Report)
async def get_report_by_report_id(id: str, user=Depends(auth.get_current_user), db=Depends(database.provide_connection)):
    try:
        res = await db.fetch_one("SELECT * FROM report WHERE id=:id", values={"id": str(id)})
        if (res is None):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found.",
            )
    except asyncpg.exceptions.DataError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed report ID.",
        )
    return res


@router.post("/", status_code=200, response_model=Report)
@limit.limit("10/minute")
async def create_report(request: Request, report: Report, user=Depends(auth.get_current_user), db=Depends(database.provide_connection)):
    async with db.transaction():
        type_value = None if report.type is None else report.type.value
        id = await db.fetch_one("INSERT INTO report (user_id, risk_level, frequency, type, description,  latitude, longitude) VALUES (:id, :risk_level, :frequency, :type, :description, :latitude, :longitude) RETURNING id", values={"id": str(dict(user)['id']), "risk_level": report.risk_level, "frequency": 1, "type": type_value, "description": report.description, "latitude": report.latitude, "longitude": report.longitude})
        return {
            "risk_level": report.risk_level,
            "type": type_value,
            "description": report.description,
            "latitude": report.latitude,
            "longitude": report.longitude,
            "id": str(dict(id)['id'])
        }


@router.patch("/{id}", status_code=200, response_model=Report)
async def update_report_by_report_id(id: str, report: PatchReport, user=Depends(auth.get_current_user), db=Depends(database.provide_connection)):
    async with db.transaction():
        if (report.latitude):
            await db.execute("UPDATE report SET latitude=:latitude WHERE id=:id", values={"latitude": report.latitude, "id": id})
        if (report.longitude):
            await db.execute("UPDATE report SET longitude=:longitude WHERE id=:id", values={"longitude": report.longitude, "id": id})
        if (report.description):
            await db.execute("UPDATE report SET description=:description WHERE id=:id", values={"description": report.description, "id": id})
        if (report.risk_level):
            await db.execute("UPDATE report SET risk_level=:risk_level WHERE id=:id", values={"risk_level": report.risk_level, "id": id})
        if (report.type):
            await db.execute("UPDATE report SET type=:type WHERE id=:id", values={"type": report.type, "id": id})
        if (report.title):
            await db.execute("UPDATE report SET title=:title WHERE id=:id", values={"title": report.title, "id": id})


@router.delete("/{id}", status_code=200)
async def delete_report_by_report_id(id: str, user=Depends(auth.get_current_user), db=Depends(database.provide_connection)):
    try:
        await db.execute("DELETE FROM report WHERE id=:id", values={"id": id})
    except asyncpg.exceptions.DataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed report ID.",
        )


async def modify_report_frequency(db, id: str, amount: int):
    async with db.transaction():
        try:
            res = await db.fetch_one("SELECT frequency FROM report WHERE id=:id", values={"id": id})
            if (res is None):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Resource not found.",
                )
            updated_frequency = int(res['frequency']) + amount
            await db.execute("UPDATE report SET frequency=:frequency WHERE id=:id", values={"frequency": updated_frequency, "id": id})
            return {
                "frequency": updated_frequency
            }
        except asyncpg.exceptions.DataError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed report ID.",
            )


@router.post("/{id}/upvote", status_code=200)
async def upvote_report(id: str, user=Depends(auth.get_current_user), db=Depends(database.provide_connection)):
    return await modify_report_frequency(db, id, 1)


@router.post("/{id}/downvote", status_code=200)
async def downvote_report(id: str, user=Depends(auth.get_current_user), db=Depends(database.provide_connection)):
    return await modify_report_frequency(db, id, -1)

@router.get("/{id}/votes", status_code=200, response_model=Frequency)
async def upvote_report(id: str, user=Depends(auth.get_current_user), db=Depends(database.provide_connection)):
    async with db.transaction():
        try:
            res = await db.fetch_one("SELECT frequency FROM report WHERE id=:id", values={"id": id})
            if (res is None):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Resource not found.",
                )
            return res
        except asyncpg.exceptions.DataError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed report ID.",
            )
