from sqlalchemy.orm import Session

from app.db.models import UserModel, LanguageModel, ProblemModel, CaseModel, SampleModel, SubmissionModel
from app.api.utils.security import get_password_hash

def seed_ini_data(db:Session):
    """注入初始数据: 管理员账户和两种语言"""

    # 注入管理员账户
    admin = db.query(UserModel).filter(UserModel.username == "admin").first()
    if admin:
        admin.username = "admin"
        admin.hashed_password = get_password_hash("admintestpassword")
        admin.role = "admin"
    else:
        admin = UserModel(
            username = "admin",
            hashed_password = get_password_hash("admintestpassword"),
            role = "admin",
        )
        db.add(admin)
    
    # 注入cpp语言
    cpp = db.query(LanguageModel).filter(LanguageModel.name == "cpp").first()
    if not cpp:
        cpp = LanguageModel(
            name = "cpp",
            file_ext = ".cpp",
            compile_cmd = "g++ -std=c++14 main.cpp -o main",
            run_cmd = "./main",
            time_limit = 1.0,
            memory_limit = 256,
        )
        db.add(cpp)
    
    # 注入python语言
    python = db.query(LanguageModel).filter(LanguageModel.name == "python").first()
    if not python:
        python = LanguageModel(
            name = "python",
            file_ext = ".py",
            run_cmd = "python main.py",
            time_limit = 2.0,
            memory_limit = 256,
        )
        db.add(python)
    
    db.commit()

def seed_other_data(db:Session):
    """注入题目和提交数据, 构建环境"""
    from app.judger.judge import eval
    from app.plagiarism.interface import build
    import time

    # 注入问题
    problem1 = ProblemModel(
        problem_id = "problem 1",
        title = "title 1",
        description = "des 1",
        input_description = "input des 1",
        output_description = "output des 1",
        constraints = "cons 1",
    )

    problem1.samples = [SampleModel(input="1 2", output="3") for _ in range(2)]
    problem1.testcases = [CaseModel(input=f"{i} {i+1}", output=f"{2*i+1}") for i in range(3)]

    problem2 = ProblemModel(
        problem_id = "problem 2",
        title = "title 2",
        description = "des 2",
        input_description = "input des 2",
        output_description = "output des 2",
        constraints = "cons 2",
    )

    problem2.samples = [SampleModel(input="1 2", output="3") for _ in range(2)]
    problem2.testcases = [CaseModel(input=f"{i} {i+1}", output=f"{2*i+1}") for i in range(3)]

    problem3 = ProblemModel(
        problem_id = "problem 3",
        title = "title 3",
        description = "des 3",
        input_description = "input des 3",
        output_description = "output des 3",
        constraints = "cons 3",
    )

    problem3.samples = [SampleModel(input="1 2", output="3") for _ in range(2)]
    problem3.testcases = [CaseModel(input=f"{i} {i+1}", output=f"{2*i+1}") for i in range(3)]

    db.add(problem1)
    db.add(problem2)
    db.add(problem3)
    db.commit()

    # 注入题目提交
    for i in range(3):
        for j in range(3):
            db_submission = SubmissionModel(
                user_id=1, _problem_id=i+1, language_id=2,
                code = "a, b = map(int, input().split())\nprint(a + b)",
            )

            db.add(db_submission)
            db.commit()
            db.refresh(db_submission)
            eval(db_submission.id)
            build(db_submission.id)
            time.sleep(2)