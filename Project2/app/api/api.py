from fastapi import APIRouter
from app.api import problems
from app.api import users
from app.api import auth
from app.api import submissions
from app.api import languages
from app.api import logs
from app.api import data
from app.api import plagiarism

api_router = APIRouter()

api_router.include_router(problems.router, prefix="/problems", tags=["Problem Management"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(auth.router, prefix="/auth", tags=["User Management"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["Submission Management"])
api_router.include_router(languages.router, prefix="/languages", tags=["Language Management"])
api_router.include_router(logs.router, prefix="/logs", tags=["Log Management"])
api_router.include_router(data.reset_router, prefix="/reset", tags=["Data Management"])
api_router.include_router(data.import_router, prefix="/import", tags=["Data Management"])
api_router.include_router(data.export_router, prefix="/export", tags=["Data Management"])
api_router.include_router(plagiarism.router, prefix="/plagiarism", tags=["Plagiarism Task Management"])