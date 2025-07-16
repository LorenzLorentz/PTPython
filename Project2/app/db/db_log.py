from sqlalchemy.orm import Session
from app.db.models import LogModel, ProblemModel
from datetime import datetime

def add_log(db:Session, user_id:int, _problem_id:int, action:str, status:int):
    """添加查询记录"""
    db_log = LogModel(user_id=user_id, _problem_id=_problem_id, action=action, status=status)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_log_list(db:Session, user_id:int, problem_id:str, offset:int, limit:int):
    """按照条件查询记录"""
    query = db.query(LogModel)

    if user_id:
        query = query.filter(LogModel.user_id == user_id)

    if problem_id:
        query = query.join(
            ProblemModel, LogModel._problem_id == ProblemModel.id
        ).filter(ProblemModel.problem_id == problem_id)

    return query.offset(offset).limit(limit).all()