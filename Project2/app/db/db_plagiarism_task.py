from sqlalchemy.orm import Session
from app.db.models import PlagiarismTaskModel
import time

def add_task(db:Session, submission_id:int, _problem_id:int, threshold:float):
    db_task = PlagiarismTaskModel(submission_id=submission_id, _problem_id=_problem_id, threshold=threshold)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    from app.plagiarism.interface import eval
    eval(db_task.id)

    return db_task

def get_task(db:Session, task_id:int):
    db_task = db.get(PlagiarismTaskModel, task_id)
    if db_task is not None:
        return db_task
    else:
        return None