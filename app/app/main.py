from typing import Optional

import databases
import sqlalchemy
from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel

# Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


import asyncio
# import asyncpg

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: str
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

# DEV database currently set up.
DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/dev"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Secrets (TODO: move to .env variables.)
SECRET_KEY = "1a2ce6eb42188da984d8bcec72cb85ad9059b2ae281d91d81a8e7ccb405858cf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create rate limiter.
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
async def startup():
    # Start database on app startup.
    try:
        await database.connect()
        print("INFO:     Successfully connected to database.")
    except ConnectionRefusedError:
        print("ERROR:    Could not connect to database.")
        raise 

@app.on_event("shutdown")
async def shutdown():
    # Stop database on shutdown.
    print("INFO:     Disconnecting from database.")
    await database.disconnect()

# Will affirm that the user exists in the database and has a valid password.
async def authenticate_user(username: str, password: str):
    valid_user = await database.fetch_one("SELECT * FROM users WHERE username=:username AND password = crypt(:password, password)", values={'username': username, 'password': password})
    if valid_user is None:
        return None
    else:
        return valid_user.id

# The short JWT will expire after a short period of time, but is required to access any important information in the DB.
async def issue_short_jwt():
    pass

# The long JWT is required to obtain a short JWT.
async def issue_long_jwt():
    pass

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/", status_code=200)
@limiter.limit("30/minute")
async def root(request: Request):
    # data = await conn.fetch("SELECT * FROM whatever")
    await authenticate_user("ethanperry247@gmail.com", "pass")
    return {"Hello": "World"}

@app.get("/user/{id}", status_code=200)
async def get_user():
    return await database.fetch_one("SELECT * FROM user_table WHERE ")

@app.post("/user", status_code=201)
@limiter.limit("2/minute")
async def create_user(request: Request, user: User):
    print(user)
    return await database.execute("INSERT INTO users (username, password, phone_number, firstname, lastname) VALUES (:username, crypt(:password, gen_salt('md5')), :phone, :first, :last)", values={'username': user.email, 'password': user.password, 'phone': user.phone, 'first': user.firstName, 'last': user.lastName})

@app.patch("/user/{id}", status_code=200)
async def update_user():
    return "Not yet implemented!"

@app.delete("/user/{id}", status_code=200)
async def delete_user():
    return "Not yet implemented!"

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
