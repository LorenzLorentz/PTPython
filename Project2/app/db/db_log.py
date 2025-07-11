from sqlalchemy.orm import Session
from app.db.models import LogModel
from datetime import datetime

def add_log(db:Session, user_id:int, _problem_id:int, action:str):
    db_log = LogModel(user_id=user_id, _problem_id=_problem_id, action=action)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_log_list(db:Session, user_id:int, _problem_id:int, offset:int, limit:int):
    query = db.query(LogModel)

    if user_id:
        query = query.filter(LogModel.user_id == user_id)

    if _problem_id:
        query = query.filter(LogModel._problem_id == _problem_id)

    return query.offset(offset).limit(limit).all()