from fastapi import APIRouter
from oj.api import problems

api_router = APIRouter()

api_router.include_router(problems.router, prefix="/problems", tags=["Problem Management"])