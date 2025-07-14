from sqlalchemy.orm import Session
from app.db.db_language import get_language_by_name
from app.db.models import SubmissionModel, StatusCategory, ProblemModel
from app.schemas.submission import SubmissionAddPayload

def add_submission(db:Session, submission:SubmissionAddPayload, _problem_id:int, language_id:int, user_id:int):
    submission_data = submission.model_dump()
    submission_data.pop("problem_id")
    submission_data.pop("language_name")
    
    db_submission = SubmissionModel(user_id=user_id, _problem_id=_problem_id, language_id=language_id, **submission_data)
    
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    
    from app.judger.tasks import eval
    eval.delay(db_submission.id)

    return db_submission

def get_submission(db:Session, submission_id:int):
    db_submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()
    return db_submission

def get_submission_list(db:Session, user_id:int, problem_id:str, status:str, page:int, page_size:int):
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
    if page is None and page_size is None:
        submissions = query.all()
    elif page is None:
        submissions = query.offset(0).limit(page_size).all()
    else:
        submissions = query.offset((page-1)*page_size).limit(page_size).all()

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

        from app.judger.tasks import eval
        eval.delay(db_submission.id)
        
        db.commit()
        db.refresh(db_submission)
        return db_submission
    return None