from fastapi import APIRouter, Depends, Request, Path
from typing import List, Annotated
from sqlalchemy.orm import Session

from app import db
from app.db.database import get_db
from app.db.models import UserModel
from app.schemas.user import(
    UserInfoResponse, UserRoleResponse, UserNameResponse, UserListResponse,
    UserAddPayload, UserQueryParams, UserRolePayload
)
from app.schemas.response import ResponseModel
from app.api.utils.permission import require_admin, require_login
from app.api.utils.exception import APIException

router = APIRouter()

@router.post("/", response_model=ResponseModel[UserInfoResponse])
async def signup(payload:UserAddPayload, db_session:Session=Depends(get_db)):
    """用户注册"""
    if len(payload.username) < 3 or len(payload.username) > 20:
        raise APIException(status_code=400, msg="用户名长度必须在3到20个字符之间")
    
    if len(payload.password) < 6:
        raise APIException(status_code=400, msg="密码长度不能少于6个字符")
    
    db_user = db.db_user.get_user_by_username(db=db_session, username=payload.username)
    if db_user:
        raise APIException(status_code=400, msg="用户名已存在")

    db_user = db.db_user.add_user(db=db_session, username=payload.username, password=payload.password, role="user")
    return {"msg": "register success", "data": db_user}

@router.post("/admin", response_model=ResponseModel[UserNameResponse])
async def signup_admin(payload:UserAddPayload, db_admin:UserModel=Depends(require_admin), db_session:Session=Depends(get_db)):
    """创建管理员账户"""
    if len(payload.username) < 3 or len(payload.username) > 40:
        raise APIException(status_code=400, msg="用户名长度必须在3到20个字符之间")
    
    if len(payload.password) < 6:
        raise APIException(status_code=400, msg="密码长度不能少于6个字符")
    
    db_user = db.db_user.get_user_by_username(db=db_session, username=payload.username)
    if db_user:
        raise APIException(status_code=400, msg="用户名已存在")

    db_user = db.db_user.add_user(db=db_session, username=payload.username, password=payload.password, role="admin")
    return {"msg": "success", "data": db_user}

@router.get("/{user_id}", response_model=ResponseModel[UserInfoResponse])
async def get_user(user_id:int, db_login:UserModel=Depends(require_login), db_session:Session=Depends(get_db)):
    """查询用户信息"""
    if db_login.role != "admin" and db_login.id != user_id:
        raise APIException(status_code=403, msg="用户无权限")
    
    db_user = db.db_user.get_user(db=db_session, user_id=user_id)
    if db_user is None:
        raise APIException(status_code=404, msg="用户不存在")
    
    return {"msg": "success", "data": db_user}

@router.put("/{user_id}/role", response_model=ResponseModel[UserRoleResponse])
async def permission_adjust(user_id:int, payload:UserRolePayload, db_admin:UserModel=Depends(require_admin), db_session:Session=Depends(get_db)):
    """用户权限变更"""
    new_role = payload.role
    if not (new_role == "admin" or new_role=="user" or new_role=="banned"):
        raise APIException(status_code=400, msg="新权限值无效")

    db_user = db.db_user.set_role(db=db_session, user_id=user_id, new_role=new_role)
    if db_user is None:
        raise APIException(status_code=404, msg="用户不存在")

    # 记录操作日志

    return {"msg": "role updated", "data": db_user}

@router.get("/", response_model=ResponseModel[UserListResponse])
async def get_user_list(params:UserQueryParams=Depends(), db_admin:UserModel=Depends(require_admin), db_session=Depends(get_db)):
    """用户列表查询"""
    result = db.db_user.get_user_list(db=db_session, offset=(params.page-1)*params.page_size, limit=params.page_size)
    return {"msg": "success", "data": result}