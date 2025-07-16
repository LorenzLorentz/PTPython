from sqlalchemy.orm import Session
from app.db.models import SubmissionModel, SubmissionStatusCategory, ProblemModel
from app.schemas.submission import SubmissionAddPayload

def add_submission(db:Session, submission:SubmissionAddPayload, _problem_id:int, language_id:int, user_id:int):
    """添加评测"""
    # 去除其他key
    submission_data = submission.model_dump()
    submission_data.pop("problem_id")
    submission_data.pop("language_name")
    
    db_submission = SubmissionModel(user_id=user_id, _problem_id=_problem_id, language_id=language_id, **submission_data)
    
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    
    # 进行评测
    from app.judger.judge import eval
    eval(db_submission.id)

    # 构建pdg
    if language_id == 2:
        from app.plagiarism.interface import build
        build(db_submission.id)

    return db_submission

def get_submission(db:Session, submission_id:int):
    """根据id查找submission"""
    db_submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()
    return db_submission

def get_submission_list(db:Session, user_id:int, problem_id:str, status:str, page:int, page_size:int):
    """根据条件查找submission"""
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
    """重新评测submission"""
    db_submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()
    if db_submission:
        db_submission.status = SubmissionStatusCategory.PENDING
        db_submission.test_case_results = []
        db_submission.time = 0.0
        db_submission.memory = 0
        db_submission.counts = 0

        from app.judger.judge import eval
        eval(db_submission.id)
        
        db.commit()
        db.refresh(db_submission)
        return db_submission
    return None