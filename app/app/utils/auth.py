# Security imports
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from ..database import database

import uuid

class Login(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    id: Optional[str] = None

# Secrets/env (TODO: move to .env variables.)
SECRET_KEY = "1a2ce6eb42188da984d8bcec72cb85ad9059b2ae281d91d81a8e7ccb405858cf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Grab bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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