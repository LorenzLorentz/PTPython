from sqlalchemy.orm import Session

from app.db.models import UserModel, ProblemModel, SubmissionModel, SampleModel, CaseModel, LanguageModel, TestCaseResultModel
from app.schemas.data import DataImport
from app.api.utils.data import seed_ini_data
from app.db.database import SessionLocal, Base, engine

def reset():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_ini_data(db)

def get_data(db:Session):
    users = db.query(UserModel).all()
    problems = db.query(ProblemModel).all()
    submissions = db.query(SubmissionModel).all()

    return {
        "users": users,
        "problems": problems,
        "submissions": submissions
    }

def set_data(db:Session, data:DataImport):
    try:
        for user in data.users:
            user_data = user.model_dump()
            user_id = user_data.pop("user_id", 0)
            db_user = UserModel(id=user_id, **user_data)
            db.merge(db_user)

        for problem in data.problems:
            problem_data = problem.model_dump()
            samples_data = problem_data.pop("samples", [])
            testcases_data = problem_data.pop("testcases", [])
            exist = db.query(ProblemModel).filter(ProblemModel.problem_id == problem.problem_id).first()

            db_problem = None
            if exist is None:
                db_problem = ProblemModel(**problem_data)
            else:
                db_problem = exist

            db_problem.samples = [SampleModel(**sample_data) for sample_data in samples_data]
            db_problem.testcases = [CaseModel(**testcase_data) for testcase_data in testcases_data]

            if exist is None:
                db.add(db_problem)

        db.commit()

        for submission in data.submissions:
            submission_data = submission.model_dump()
            
            problem_id = submission_data.pop("problem_id")
            db_problem = db.query(ProblemModel).filter(ProblemModel.problem_id == problem_id).first()
            language_name = submission_data.pop("language_name")
            db_language = db.query(LanguageModel).filter(LanguageModel.name == language_name).first()
            
            test_case_results_data = submission_data.pop("test_case_results", [])
            
            db_submission = SubmissionModel(user_id=submission.user_id, _problem_id=db_problem.id, language_id=db_language.id, **submission_data)
            db_submission.test_case_results = [TestCaseResultModel(**test_case_result_data) for test_case_result_data in test_case_results_data]

            db.merge(db_submission)
        
        db.commit()
    
    except Exception as e:
        with open("error.log", "a") as f:
            print(e, file=f)

        db.rollback()
        raise e