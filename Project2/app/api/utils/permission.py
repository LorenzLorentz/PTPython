from fastapi import Request
from sqlalchemy.orm import Session
from app import db

def check_admin(request:Request, db_session:Session) -> bool:
    user_id = request.session.get("user_id")
    db_user = db.db_user.get_user(db=db_session, user_id=user_id)
    
    if db_user is None:
        return False
    
    return db_user.role == "admin"

def check_login(request:Request, db_session:Session) -> bool:
    user_id = request.session.get("user_id")

    if user_id is None:
        return False

    db_user = db.db_user.get_user(db=db_session, user_id=user_id)
    
    return db_user is not None

def check_self(request:Request, user_id:int) -> bool:
    return user_id == request.session.get("user_id")

def check_banned(request:Request, db_session:Session) -> bool:
    user_id = request.session.get("user_id")
    db_user = db.db_user.get_user(db=db_session, user_id=user_id)

    if db_user:
        return db_user.role == "banned"
    else:
        return False

from fastapi import Request, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db 
from app.db.models import UserModel
from app import db
from app.api.utils.exception import APIException

def get_current_user(request:Request, db_session:Session=Depends(get_db)) -> Optional[UserModel]:
    user_id = request.session.get("user_id")
    if not user_id:
        return None

    user = db.db_user.get_user(db=db_session, user_id=user_id)
    return user

def is_admin(user:Optional[UserModel]) -> bool:
    """检查用户对象是否为管理员。"""
    return user is not None and user.role == "admin"

def is_logged_in(user: Optional[UserModel]) -> bool:
    """检查用户对象是否登录"""
    return user is not None

def is_banned(user: Optional[UserModel]) -> bool:
    """检查用户对象是否被封禁。"""
    return user is not None and user.role == "banned"

def require_login(current_user:UserModel=Depends(get_current_user)):
    if not is_logged_in(current_user):
        raise APIException(status_code=401, msg="用户未登录")
    return current_user

def require_admin(current_user:UserModel=Depends(get_current_user)):
    if not is_logged_in(current_user):
        raise APIException(status_code=401, msg="用户未登录")
    if not is_admin(current_user):
        raise APIException(status_code=403, msg="用户无权限")
    return current_user

def require_notbanned(current_user:UserModel=Depends(get_current_user)):
    if not is_logged_in(current_user):
        raise APIException(status_code=401, msg="未登录")
    if is_banned(current_user):
        raise APIException(status_code=403, msg="用户被禁用")
    return current_user