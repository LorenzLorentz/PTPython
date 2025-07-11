from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from app import db
from app.db.database import get_db
from app.schemas.response import ResponseModel
from app.schemas.user import UserAddPayload, UserBriefResponse
from app.api.utils.security import verify_password
from app.api.utils.permission import check_login
from app.api.utils.exception import APIException

router = APIRouter()

@router.post("/login", response_model=ResponseModel[UserBriefResponse])
async def login(request:Request, payload:UserAddPayload, db_session=Depends(get_db)):
    """用户登陆"""
    db_user = db.db_user.get_user_by_username(db=db_session, username=payload.username)

    if db_user is None:
        raise APIException(status_code=401, msg="用户名或密码错误")
    
    if not verify_password(plain_password=payload.password, hashed_password=db_user.hashed_password):
        raise APIException(status_code=401, msg="用户名或密码错误")
    
    if db_user.role == "banned":
        raise APIException(status_code=403, msg="用户被禁用")
    
    request.session["user_id"] = db_user.id

    return {"msg": "login success", "data": db_user}

@router.post("/logout", response_model=ResponseModel[None])
async def logout(request:Request, db_session=Depends(get_db)):
    """用户登出"""
    if not check_login(request=request, db_session=db_session):
        raise APIException(status_code=401, msg="未登录")
    request.session.pop("user_id")
    return {"msg": "logout success", "data": None}