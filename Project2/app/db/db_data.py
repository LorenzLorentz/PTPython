from sqlalchemy.orm import Session

from app.db.models import UserModel, ProblemModel, SubmissionModel
from app.schemas.data import DataExport
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

def set_data(db:Session, data:DataExport):
    try:
        user_map = {} # key: username, value: user_db_id
        problem_map = {} # key: problem_source_id or title, value: problem_db_id

        for user in data.users: # 不提供主键
            existing_user = db.query(UserModel).filter(UserModel.username == user.username).first()

            if existing_user:
                # 用户已存在，直接将数据库中的ID存入map
                user_map[user_data.username] = existing_user.id
                # 可选：如果需要，可以在这里用新数据更新旧用户
                # existing_user.email = user_data.email
                # db.add(existing_user)
            else:
                new_user = UserModel(**user_data.model_dump(exclude={'id'}))
                db.add(new_user)
                # 重要：必须 flush 来获取新生成的 ID，但不要 commit
                db.flush() 
                user_map[user_data.username] = new_user.id

            user_data = user.model_dump()
            
            username = user_data.pop("username")
            hashed_password = user_data.pop("password", "")
            role = user_data.pop("role", "user")
            db_user = UserModel(username=username, hashed_password=hashed_password, role=role, **user_data)
            
            db.merge(db_user)

        for problem in data.problems: # 主键不作为判重标准
            problem_data= problem.model_dump()
            testcases_data = problem_data.pop("testcases", [])
            samples_data = problem_data.pop("samples", [])
            db_problem = ProblemModel(**problem_data)
            db_problem.testcases = [CaseModel(**case) for case in testcases_data]
            db_problem.samples = [SampleModel(**sample) for sample in samples_data]
            problem_model = ProblemModel(**problem_data)
            db.merge(problem_model)

        for submission_data in data.submissions:
            submission_model = SubmissionModel(**submission_data.model_dump())
            db.merge(submission_model)
        
        db.commit()
    
    except Exception as e:
        db.rollback()
        raise e