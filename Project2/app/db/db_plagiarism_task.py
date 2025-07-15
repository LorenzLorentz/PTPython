from sqlalchemy.orm import Session
from app.db.models import PlagiarismTaskModel
from app.api.utils.security import get_password_hash

def add_task(db:Session, submission_id:int, problem_id:int, thresold:float):
    db_task = PlagiarismTaskModel(submission_id=submission_id, problem_id=problem_id, thresold=thresold)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    from app.plagiarism.interface import eval
    eval(db_task.id)

    return db_task

def get_task(db:Session, task_id:int):
    db_task = db.get(PlagiarismTaskModel, task_id)
    return db_task