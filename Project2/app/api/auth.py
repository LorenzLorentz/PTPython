from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from app import db
from app.db.database import get_db
from app.schemas.response import ResponseModel
from app.schemas.user import User, UserAddPayload, UserBrief
from app.api.utils.security import verify_password

router = APIRouter()

@router.post("/login", response_model=ResponseModel[UserBrief])
async def login(request:Request, payload:UserAddPayload, db_session=Depends(get_db)):
    """用户登陆"""
    db_user = db.db_user.get_user_by_username(db=db_session, username=payload.username)

    if db_user is None:
        raise HTTPException(status_code=400, detail="用户名或密码错误") # 用户不存在
    
    if not verify_password(plain_password=payload.password, hashed_password=db_user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误") # 密码错误
    
    if db_user.role == "banned":
        raise HTTPException(status_code=403, detail="用户被禁用")
    
    request.session["user_id"] = db_user.user_id

    return {"msg": "login success", "data": db_user}

@router.post("/logout", response_model=ResponseModel[None])
async def logout(request:Request):
    """用户登出"""
    if "user_id" not in request.session:
        raise HTTPException(status_code=401, detail="未登录")
    request.session.pop("user_id")
    return {"msg": "logout success", "data": None}