from typing import Optional

from fastapi import FastAPI

import asyncio
import asyncpg

import cole

app = FastAPI()

async def run():
    print("Initializing database connection.")
    conn = await asyncpg.connect(user='postgres', password='postgres', host='127.0.0.1', port='5432')
    
    return conn

@app.get("/{item}")
async def read_root():
    conn = await run()
    data = await conn.fetch("SELECT * FROM whatever")
    return {"Hello": data}

# loop = asyncio.get_event_loop()
# loop.run_until_complete(run())
