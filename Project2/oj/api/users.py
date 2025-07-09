from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from oj import db
from oj.db.database import get_db
from oj.schemas.user import User, UserAdd, UserID, UserInfo, UserRole, UserQuery
from oj.schemas.response import ResponseModel
from oj.api.permission import check_admin

router = APIRouter()

@router.post("/", response_model=ResponseModel[UserID])
async def signup(user:UserAdd, db_session=Depends(get_db)):
    """用户注册"""
    if len(user.username) < 3 or len(user.username) > 20:
        raise HTTPException(status_code=400, detail="用户名已存在/参数错误")
    
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="用户名已存在/参数错误")
    
    db_user = db.db_user.get_user_by_username(db=db_session, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在/参数错误")

    db_user = db.db_user.add_user(db=db_session, user=user)
    return {"msg": "register success", "data": db_user}

@router.get("/{user_id}", response_model=ResponseModel[UserInfo])
async def get_user(request:Request, user:UserID, db_session=Depends(get_db)):
    """查询用户信息"""
    if not check_admin(request=request, db_session=db_session):
        raise HTTPException(status_code=403, detail="权限不足")
    
    db_user = db.db_user.get_user(db=db_session, user_id=user.user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"msg": "success", "data": db_user}

@router.put("/{user_id}/role", response_model=ResponseModel[UserRole])
async def permission_adjust(request:Request, user:UserRole, db_session=Depends(get_db)):
    """用户权限变更"""
    if not check_admin(request=request, db_session=db_session):
        raise HTTPException(status_code=403, detail="权限不足")

    new_role = user.role
    if not (new_role == "admin" or new_role=="user" or new_role=="banned"):
        raise HTTPException(status_code=400, detail="缺少/错误参数")

    db_user = db.db_user.set_role(db=db_session, user_id=user.user_id, new_role=new_role)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 记录操作日志

    return {"msg": "role updated", "data": db_user}

@router.get("/users", response_model=ResponseModel)
async def get_user_list(request:Request, user:UserQuery, db_session=Depends(get_db)):
    """用户列表查询"""
    if not check_admin(request=request, db_session=db_session):
        raise HTTPException(status_code=403, detail="权限不足")
    
    db_user_list = db.db_user.get_user_list(db=db_session, username=user.username, role=user.role, offset=user.page*user.page_size, limit=user.page_size)
    
    return {"msg": "success", "data": {"total": len(db_user_list), "users": db_user_list}}