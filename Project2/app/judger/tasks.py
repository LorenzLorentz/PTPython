from .celery_app import celery_app
from app.db.database import SessionLocal
from app.schemas.submission import TestCaseResult
from app.db.models import SubmissionModel, StatusCategory

RESULTDICT_itoe = [
    StatusCategory.AC,
    StatusCategory.WA,
    StatusCategory.RE,
    StatusCategory.TLE,
    StatusCategory.MLE,
    StatusCategory.PENDING,
    StatusCategory.JUDGING,
    StatusCategory.ERROR,
]

RESULTDICT_stoi = {
    "AC": 0,
    "WA": 1,
    "RE": 2,
    "TLE": 3,
    "MLE": 4,
    "pending": 5,
    "judging": 6,
    "error": 7,
}

@celery_app.task
def judge_submission(submission_id: int):
    db = SessionLocal()
    
    try:
        db_submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()
        if not db_submission:
            return

        db_submission.status = StatusCategory.JUDGING
        db.commit()

        test_case_results:list[TestCaseResult] = [] # 进行评测

        db_submission.status = RESULTDICT_itoe[max([RESULTDICT_stoi[test_case_result.result] for test_case_result in test_case_results])]
        db_submission.time = max([test_case_result.time for test_case_result in test_case_results])
        db_submission.memory = max([test_case_result.memory for test_case_result in test_case_results])
        db_submission.counts = db_submission.score * db_submission.counts = db_submission.score * sum(1 for test_case_result in test_case_results if test_case_result.result == "AC")
        
        db.commit()
    except Exception as e:
        db.rollback()
        db_submission = db.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()
        db_submission.status = StatusCategory.ERROR
        db.commit()
    finally:
        db.close()