from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter
from ..database import database
from ..utils import limiter

from typing import Optional
from datetime import datetime, timedelta

from fastapi import Request, Depends, HTTPException, status
from pydantic import BaseModel

# Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

import uuid

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Login(BaseModel):
    username: str
    password: str

class User(BaseModel):
    firstname: str
    lastname: str
    username: str
    phone: str

class CreateUser(User):
    password: str


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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


limit = limiter.provide_limiter()
router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

# Secrets/env (TODO: move to .env variables.)
SECRET_KEY = "1a2ce6eb42188da984d8bcec72cb85ad9059b2ae281d91d81a8e7ccb405858cf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Will authenticate user against password hash in the db, and will return user id if so.
async def authenticate_user(login: Login, db=Depends(database.provide_connection)):
    valid_user = await db.fetch_one(query="SELECT * FROM users WHERE username=:username AND password = crypt(:password, password)", values={'username': login.username, 'password': login.password})
    if valid_user is None:
        return None
    else:
        return str(dict(valid_user)['id'])

# Will create a user JWT token.
async def create_access_token(data: dict, expiry: Optional[timedelta] = None):
    encode = data.copy()
    if expiry:
        expire = datetime.utcnow() + expiry
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)

    encode.update({"exp": expire})
    user_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return user_jwt

# Will use decode a JWT token to verify user.
async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(database.provide_connection)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        if id is None:
            raise credentials_exception
        token_data = TokenData(id=id)
    except JWTError:
        raise credentials_exception
    user = await db.fetch_one(
        "SELECT firstname, lastname, username, phone FROM users WHERE id=:id", values={"id": uuid.UUID(id)})
    if user is None:
        raise credentials_exception
    return dict(user)

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
    # if (await db.execute()):
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="User already exists"
    #     )
    # TODO: decide whether or not to allow users with the same username.
    async with db.transaction():
        await db.execute("INSERT INTO users (username, password, phone, firstname, lastname) VALUES (:username, crypt(:password, gen_salt('md5')), :phone, :first, :last)", values={'username': user.username, 'password': user.password, 'phone': user.phone, 'first': user.firstname, 'last': user.lastname})

# Update user information.
@router.patch("/{id}", status_code=200)
async def update_user(id: int):
    return "Not yet implemented!"

# Delete user.
@router.delete("/{id}", status_code=200)
async def delete_user(id: int):
    return "Not yet implemented!"