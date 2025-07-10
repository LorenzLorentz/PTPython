from sqlalchemy.orm import Session
from oj.db.models import LogModel
from datetime import datetime

def add_log(db:Session, user_id:int, problem_id:str, action:str, time:datetime):
    db_log = LogModel(user_id=user_id, problem_id=problem_id, action=action, time=time)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def add_log_list(db:Session, user_id:int, problem_id_list:list[str], action:str, time:datetime):
    for problem_id in problem_id_list:
        add_log(db, user_id, problem_id, action, time)

def get_log_list(db:Session, user_id:int, problem_id:str, offset:int, limit:int):
    query = db.query(LogModel)

    if user_id:
        query = query.filter(LogModel.user_id == user_id)

    if problem_id:
        query = query.filter(LogModel.problem_id == problem_id)

    return query.offset(offset).limit(limit)