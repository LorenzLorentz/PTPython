from fastapi import APIRouter, Depends, HTTPException, Request, Path
from typing import List, Annotated

from oj import db
from oj.db.database import get_db
from oj.schemas.user import User, UserAddPayload, UserID, UserInfo, UserRole, UserQueryPayload, UserRolePayload
from oj.schemas.response import ResponseModel
from oj.api.utils.permission import check_admin

router = APIRouter()

@router.get("/access")
async def get_access_log_list():
    """日志访问审计"""
    pass