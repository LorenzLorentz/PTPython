from fastapi import FastAPI
from oj.api.api import api_router

app = FastAPI(title="OJ System")

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to OJ System API"}