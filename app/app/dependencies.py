from fastapi import Header, HTTPException

async def get_bearer_toekn(token: str = Header(...)):
    if token != "bearer":
        raise HTTPException(status_code=400, detail="bearer header invalid")