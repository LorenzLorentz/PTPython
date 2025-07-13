from sqlalchemy.orm import Session
from app.db.db_language import get_language_by_name
from app.db.models import SubmissionModel, StatusCategory, ProblemModel
from app.schemas.submission import SubmissionAddPayload

def add_submission(db:Session, submission:SubmissionAddPayload, _problem_id:int, user_id:int):
    submission_data = submission.model_dump()
    submission_data.pop("problem_id")
    language_name = submission_data.pop("language_name")
    language = get_language_by_name(db=db, name=language_name)
    
    if language:
        db_submission = SubmissionModel(user_id=user_id, _problem_id=_problem_id, language_id=language.id, **submission_data)
    else:
        with open("error.log", "a") as f:
            print(language_name, file=f)
        return None
    
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    
    # from app.judger.tasks import eval
    # eval.delay(db_submission.id)

    return db_submission

def get_submission(db:Session, submission_id:int):
    db_submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()
    return db_submission

def get_submission_list(db:Session, user_id:int, problem_id:str, status:str, offset:int, limit:int):
    query = db.query(SubmissionModel)

    if user_id:
        query = query.filter(SubmissionModel.user_id == user_id)

    if problem_id:
        query = query.join(
            ProblemModel, SubmissionModel._problem_id == ProblemModel.id
        ).filter(ProblemModel.problem_id == problem_id)
    
    if status:
        query = query.filter(SubmissionModel.status == status)

    total = query.count()
    submissions = query.offset(offset).limit(limit).all()

    return {
        "total": total,
        "submissions": submissions,
    }

def reset_submission(db:Session, submission_id:int):
    db_submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()
    if db_submission:
        db_submission.status = StatusCategory.PENDING
        db_submission.test_case_results = []
        db_submission.time = 0.0
        db_submission.memory = 0
        db_submission.counts = 0
        
        db.commit()
        db.refresh(db_submission)
        return db_submission
    return None