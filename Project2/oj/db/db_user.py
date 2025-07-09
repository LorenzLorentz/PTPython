from sqlalchemy.orm import Session
from oj.db.models import User as UserModel
from oj.schemas.user import UserAdd, UserRole

def get_user(db:Session, user_id:int):
    return db.query(UserModel).filter(UserModel.user_id == user_id).first()

def get_user_by_username(db:Session, username:str):
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user_list(db:Session, username:str, role:str, offset:int, limit:int):
    query = db.query(UserModel)

    if username:
        query = query.filter(UserModel.username == username)

    if role:
        query = query.filter(UserModel.role == role)

    return query.offset(offset).limit(limit).all()

def add_user(db:Session, user:UserAdd):
    db_user = UserModel()
    db.add(user)
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