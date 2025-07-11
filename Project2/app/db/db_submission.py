from sqlalchemy.orm import Session
from app.db.models import SubmissionModel
from app.schemas.submission import SubmissionAddPayload
from app.schemas.problem import Problem

def add_submission(db:Session, submission:SubmissionAddPayload, problem:Problem, user_id:int):
    db_submission = SubmissionModel(user_id=user_id, testcases=problem.testcases, **submission.model_dump())
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def get_submission(db:Session, submission_id:int):
    return db.query(SubmissionModel).filter(SubmissionModel.submission_id == submission_id).first()

def get_submission_list(db:Session, user_id:int, problem_id:str, status:str, offset:int, limit:int):
    query = db.query(SubmissionModel)

    if user_id:
        query = query.filter(SubmissionModel.user_id == user_id)

    if problem_id:
        query = query.filter(SubmissionModel.problem_id == problem_id)

    if status:
        query = query.filter(SubmissionModel.status == status)

    total = query.count()
    submissions = query.offset(offset).limit(limit)

    return {
        "total": total,
        "submissions": submissions,
    }

def reset_submission(db:Session, submission_id:int):
    db_submission = db.query(SubmissionModel).filter(SubmissionModel.submission_id == submission_id).first()
    if db_submission:
        db_submission.status = "Pending"
        db_submission.status_detail = "[]"
        db_submission.time = 0.0
        db_submission.memory = 0
        db_submission.counts = 0
        
        db.commit()
        db.refresh(db_submission)
        return db_submission
    return None