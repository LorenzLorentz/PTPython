from fastapi import FastAPI

app = FastAPI(
    title="Simple OJ System - Student Template",
    description="A simple online judge system for programming assignments",
    version="1.0.0"
)

@app.get("/")
async def welcome():
    return "Welcome!"
