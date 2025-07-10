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
    db_user = db.db_user.get_user(db=db_session, user_id=user_id)

    if db_user:
        return True
    else:
        return False
    
def check_banned(request:Request, db_session:Session) -> bool:
    user_id = request.session.get("user_id")
    db_user = db.db_user.get_user(db=db_session, user_id=user_id)

    if db_user:
        return db_user.role == "banned"
    else:
        return True