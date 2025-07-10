from sqlalchemy.orm import Session
from app.db.models import UserModel
from app.api.utils.security import get_password_hash

def get_user(db:Session, user_id:int):
    return db.query(UserModel).filter(UserModel.user_id == user_id).first()

def get_user_by_username(db:Session, username:str):
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user_list(db:Session, offset:int, limit:int):
    query = db.query(UserModel)
    
    total = query.count()
    users = query.offset(offset).limit(limit).all()
    
    return {"total": total, "users": users}

def add_user(db:Session, username:str, password:str, role:str):
    db_user = UserModel(username=username, password=get_password_hash(password), role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def set_role(db:Session, user_id:int, new_role:str):
    user_to_update = db.query(UserModel).filter(UserModel.user_id == user_id).first()

    if user_to_update:
        user_to_update.role = new_role
        db.commit()
        db.refresh(user_to_update)
        
    return user_to_update