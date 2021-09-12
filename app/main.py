from typing import Optional

from fastapi import FastAPI

import cole

app = FastAPI()

@app.get("/{item}")
def read_root():
    return {"Hello": "World"}

