from sqlalchemy.orm import Session

from app.db.models import UserModel, ProblemModel, SubmissionModel
from app.schemas.data import DataBase
from app.api.utils.data import seed_ini_data

def reset(db:Session):
    try:
        db.query(SubmissionModel).delete(synchronize_session=False)
        db.query(ProblemModel).delete(synchronize_session=False)
        db.query(UserModel).delete(synchronize_session=False)

        seed_ini_data(db)

        db.commit()
    except Exception as e:
        db.rollback()
        raise e

def get_data(db:Session):
    users = db.query(UserModel).all()
    problems = db.query(ProblemModel).all()
    submissions = db.query(SubmissionModel).all()

    return {
        "users": users,
        "problems": problems,
        "submissions": submissions
    }

def set_data(db:Session, data:DataBase):
    try:
        for user_data in data.users:
            user_model = UserModel(**user_data.model_dump())
            db.merge(user_model)

        for problem_data in data.problems:
            problem_model = ProblemModel(**problem_data.model_dump())
            db.merge(problem_model)

        db.commit()

        for submission_data in data.submissions:
            submission_model = SubmissionModel(**submission_data.model_dump())
            db.merge(submission_model)
        
        db.commit()
    
    except Exception as e:
        db.rollback()
        raise e