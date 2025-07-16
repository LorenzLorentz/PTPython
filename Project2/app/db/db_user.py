from sqlalchemy.orm import Session
from app.db.models import UserModel
from app.api.utils.security import get_password_hash

def get_user(db:Session, user_id:int):
    """根据id查找user"""
    return db.get(UserModel, user_id)

def get_user_by_username(db:Session, username:str):
    """根据name查找user"""
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user_list(db:Session, offset:int, limit:int):
    """根据offset和limit获取user"""
    query = db.query(UserModel)
    
    total = query.count()
    users = query.offset(offset).limit(limit).all()
    
    return {"total": total, "users": users}

def add_user(db:Session, username:str, password:str, role:str):
    """添加user"""
    db_user = UserModel(username=username, hashed_password=get_password_hash(password), role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def set_role(db:Session, user_id:int, new_role:str):
    """设置用户权限"""
    user_to_update = db.get(UserModel, user_id)

    if user_to_update:
        user_to_update.role = new_role
        db.commit()
        db.refresh(user_to_update)
        
    return user_to_update