from fastapi import APIRouter, Depends, HTTPException, Request, Path
from typing import List, Annotated

from app import db
from app.db.database import get_db
from app.schemas.user import User, UserAddPayload, UserID, UserInfo, UserRole, UserQueryPayload, UserRolePayload
from app.schemas.response import ResponseModel
from app.api.utils.permission import check_admin

router = APIRouter()

@router.post("/", response_model=ResponseModel[UserID])
async def signup(payload:UserAddPayload, db_session=Depends(get_db)):
    """用户注册"""
    if len(payload.username) < 3 or len(payload.username) > 20:
        raise HTTPException(status_code=400, detail="用户名已存在/参数错误") # 用户名长度必须在3到20个字符之间
    
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="用户名已存在/参数错误") # 密码长度不能少于6个字符
    
    db_user = db.db_user.get_user_by_username(db=db_session, username=payload.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在/参数错误") # 用户名已存在

    db_user = db.db_user.add_user(db=db_session, username=payload.username, password=payload.password)
    return {"msg": "register success", "data": db_user}

@router.get("/{user_id}", response_model=ResponseModel[UserInfo])
async def get_user(request:Request, user_id:int, db_session=Depends(get_db)):
    """查询用户信息"""
    if not check_admin(request=request, db_session=db_session):
        raise HTTPException(status_code=403, detail="权限不足")
    
    db_user = db.db_user.get_user(db=db_session, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"msg": "success", "data": db_user}

@router.put("/{user_id}/role", response_model=ResponseModel[UserRole])
async def permission_adjust(request:Request, user_id:int, payload:UserRolePayload, db_session=Depends(get_db)):
    """用户权限变更"""
    if not check_admin(request=request, db_session=db_session):
        raise HTTPException(status_code=403, detail="权限不足")

    new_role = payload.role
    if not (new_role == "admin" or new_role=="user" or new_role=="banned"):
        raise HTTPException(status_code=400, detail="缺少/错误参数") # 新权限值无效(如user、admin、banned)

    db_user = db.db_user.set_role(db=db_session, user_id=user_id, new_role=new_role)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 记录操作日志

    return {"msg": "role updated", "data": db_user}

@router.get("/users", response_model=ResponseModel[UserInfo])
async def get_user_list(request:Request, payload:UserQueryPayload, db_session=Depends(get_db)):
    """用户列表查询"""
    if not check_admin(request=request, db_session=db_session):
        raise HTTPException(status_code=403, detail="权限不足")
    
    result = db.db_user.get_user_list(
        db=db_session, offset=payload.page*payload.page_size, limit=payload.page_size
    )
    
    return {"msg": "success", "data": result}