from fastapi import Request, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db 
from app.db.models import UserModel
from app import db
from app.api.utils.exception import APIException

def get_current_user(request:Request, db_session:Session=Depends(get_db)) -> Optional[UserModel]:
    """获取当前用户"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    user = db.db_user.get_user(db=db_session, user_id=user_id)
    return user

def is_admin(user:Optional[UserModel]) -> bool:
    """检查用户是否为管理员。"""
    return user is not None and user.role == "admin"

def is_logged_in(user: Optional[UserModel]) -> bool:
    """检查用户是否登录"""
    return user is not None

def is_banned(user: Optional[UserModel]) -> bool:
    """检查用户是否被封禁。"""
    return user is not None and user.role == "banned"

def require_login(current_user:UserModel=Depends(get_current_user)):
    """Depends方法, 检查是否登录"""
    if not is_logged_in(current_user):
        raise APIException(status_code=401, msg="用户未登录")
    return current_user

def require_admin(current_user:UserModel=Depends(get_current_user)):
    """Depends方法, 检查是否为管理员"""
    if not is_logged_in(current_user):
        raise APIException(status_code=401, msg="用户未登录")
    if not is_admin(current_user):
        raise APIException(status_code=403, msg="用户无权限")
    return current_user

def require_notbanned(current_user:UserModel=Depends(get_current_user)):
    """Depends方法, 检查是否被封禁"""
    if not is_logged_in(current_user):
        raise APIException(status_code=401, msg="未登录")
    if is_banned(current_user):
        raise APIException(status_code=403, msg="用户被禁用")
    return current_user