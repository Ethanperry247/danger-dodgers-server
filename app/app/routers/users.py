from typing import Optional
from datetime import datetime, timedelta
from databases.core import Database
from fastapi import APIRouter
from ..database import database
from ..utils import limiter
from ..utils.auth import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_user, Login

from typing import Optional
from datetime import datetime, timedelta

from fastapi import Request, Depends, HTTPException, status
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    firstname: str
    lastname: str
    username: str
    phone: str

class CreateUser(User):
    password: str

class PatchUser(BaseModel):
    username: str
    password: str
    newUsername: Optional[str] = None
    newPassword: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None

class HazardType(BaseModel):
    type: str


class Hazard(BaseModel):
    riskLevel: int
    frequency: int
    hazardType: HazardType
    desc: str


class HazardArea(BaseModel):
    hazard: Hazard
    latitude: float
    longitude: float
    altitude: float

limit = limiter.provide_limiter()
router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

@router.post("/refresh", response_model=Token)
async def refresh_token(user = Depends(get_current_user)):
    if (user):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await create_access_token(
            data={"id": str(dict(user)['id'])}, expiry=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(auth_id: str = Depends(authenticate_user)):
    if not auth_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"id": auth_id}, expiry=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Will fetch information about current user.
@router.get("/", status_code=200, response_model=User)
async def get_user(user: str = Depends(get_current_user)):
    return user

# Create a new user.
@router.post("/", status_code=201)
@limit.limit("2/minute")
async def create_user(request: Request, user: CreateUser, db=Depends(database.provide_connection)):
    user_exists = await db.fetch_one("SELECT * FROM users WHERE username=:username", values={'username': user.username})
    if (user_exists):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    async with db.transaction():
        await db.execute("INSERT INTO users (username, password, phone, firstname, lastname) VALUES (:username, crypt(:password, gen_salt('md5')), :phone, :first, :last)", values={'username': user.username, 'password': user.password, 'phone': user.phone, 'first': user.firstname, 'last': user.lastname})

# Update user information.
@router.patch("/", status_code=200)
async def update_user(updated_user: PatchUser, current_user: User = Depends(get_current_user), db = Depends(database.provide_connection)):
    auth = await authenticate_user(login=Login(**{"username": updated_user.username, "password": updated_user.password}))
    if (not auth):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    async with db.transaction():
        if (updated_user.newPassword):
            await db.execute("UPDATE users SET password=crypt(:password, gen_salt('md5')) WHERE id=:id", values={"password": updated_user.newPassword, "id": auth})
        if (updated_user.newUsername):
            await db.execute("UPDATE users SET username=:username WHERE id=:id", values={"username": updated_user.newUsername, "id": auth})
        if (updated_user.firstname):
            await db.execute("UPDATE users SET firstname=:firstname WHERE id=:id", values={"firstname": updated_user.firstname, "id": auth})
        if (updated_user.lastname):
            await db.execute("UPDATE users SET lastname=:lastname WHERE id=:id", values={"lastname": updated_user.lastname, "id": auth})
        if (updated_user.phone):
            await db.execute("UPDATE users SET phone=:phone WHERE id=:id", values={"phone": updated_user.phone, "id": auth})

# Delete user upon auth.
@router.delete("/", status_code=200)
async def delete_user(login: Login, current_user: User = Depends(get_current_user), db: Database = Depends(database.provide_connection)):
    auth = await authenticate_user(login=Login(**{"username": login.username, "password": login.password}))
    if (not auth):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    async with db.transaction():
        db.execute("DELETE FROM users WHERE id=:id", values={"id":auth})
