from fastapi import APIRouter
from oj.api import problems
from oj.api import users
from oj.api import auth
from oj.api import submissions
from oj.api import languages
from oj.api import logs

api_router = APIRouter()

api_router.include_router(problems.router, prefix="/problems", tags=["Problem Management"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(auth.router, prefix="/auth", tags=["User Management"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["Submission Management"])
api_router.include_router(languages.router, prefix="/languages", tags=["Language Management"])
api_router.include_router(logs.router, prefix="/log", tags=["Log Management"])