from fastapi import APIRouter, Depends, Request
from typing import List
from sqlalchemy.orm import Session

from app import db
from app.db.database import get_db
from app.db.models import UserModel
from app.schemas.response import ResponseModel
from app.schemas.user import UserAddPayload, UserBriefResponse
from app.api.utils.security import verify_password
from app.api.utils.permission import require_login
from app.api.utils.exception import APIException

router = APIRouter()

@router.post("/login", response_model=ResponseModel[UserBriefResponse])
async def login(request:Request, payload:UserAddPayload, db_session:Session=Depends(get_db)):
    """
    用户登陆 
    参数: username (str, 必填), password (str, 必填) 
    权限: 无
    """
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
async def logout(request:Request, db_login:UserModel=Depends(require_login), db_session:Session=Depends(get_db)):
    """
    用户登出
    参数: 无
    权限: 登录用户
    """
    request.session.pop("user_id")
    return {"msg": "logout success", "data": None}