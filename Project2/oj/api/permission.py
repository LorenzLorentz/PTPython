from fastapi import Request
from sqlalchemy.orm import Session
from oj import db

def check_admin(request:Request, db_session:Session) -> bool:
    user_id = request.session.get("user_id")
    db_user = db.db_user.get_user(db=db_session, user_id=user_id)
    
    if db_user is None:
        return False
    
    if db_user.role is not "admin":
        return False
    
    return True