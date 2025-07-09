from fastapi import APIRouter, Depends, HTTPException
from typing import List

from oj import db
from oj.db.database import get_db
from oj.schemas.response import ResponseModel
from oj.schemas.user import User, UserBrief

router = APIRouter()

@router.post("/login", response_model=ResponseModel[UserBrief])
async def login(username:str, password:str, db_session=Depends(get_db)):
    """用户登陆"""
    db_user = db.db_user.get_user_by_username(username=username)

    if db_user is None:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    if db_user.password != password:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    return {"msg": "login success", "data": db_user}

@router.post("/logout")
async def logout(username:str, password:str):
    """用户登出"""
    pass