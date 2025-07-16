from sqlalchemy.orm import Session
from app.db.models import ProblemModel, CaseModel, SampleModel
from app.schemas.problem import ProblemAddPayload

def get_problem(db:Session, problem_id:str):
    """按照problem_id查询题目"""
    return db.query(ProblemModel).filter(ProblemModel.problem_id == problem_id).first()

def get_problem_by_id(db:Session, _problem_id:int):
    """按照id查询题目"""
    return db.get(ProblemModel, _problem_id)

def get_problem_list(db:Session):
    """获取所有题目"""
    return db.query(ProblemModel).all()

def add_problem(db:Session, problem:ProblemAddPayload):
    """添加题目"""
    # 去除其他key
    problem_data = problem.model_dump()
    testcases_data = problem_data.pop("testcases", [])
    samples_data = problem_data.pop("samples", [])
    spj_language_name = problem_data.pop("spj_language_name", "")
    
    db_problem = ProblemModel(**problem_data)
    db_problem.testcases = [CaseModel(**case) for case in testcases_data]
    db_problem.samples = [SampleModel(**sample) for sample in samples_data]
    
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem

def delete_problem(db:Session, problem_id:str):
    """删除题目"""
    db_problem = db.query(ProblemModel).filter(ProblemModel.problem_id == problem_id).first()
    if db_problem:
        db.delete(db_problem)
        db.commit()
        return db_problem
    return None

def set_problem_log_visibility(db:Session, problem_id:str, log_visibility:bool):
    """设置题目日志可见性"""
    db_problem = db.query(ProblemModel).filter(ProblemModel.problem_id == problem_id).first()
    if db_problem:
        db_problem.log_visibility = log_visibility
        db.commit()
        db.refresh(db_problem)
        return db_problem
    return None

def set_problem_judge_mode(db:Session, problem_id:str, judge_mode:str):
    """设置题目评测模式"""
    db_problem = db.query(ProblemModel).filter(ProblemModel.problem_id == problem_id).first()
    if db_problem:
        db_problem.judge_mode = judge_mode
        if judge_mode != "spj":
            db_problem.spj_code = None
            db_problem.spj_language_id = None
        db.commit()
        db.refresh(db_problem)
        return db_problem
    return None

def add_spj(db:Session, problem_id:str, language_id:int, code:str):
    """增加spj脚本"""
    db_problem = db.query(ProblemModel).filter(ProblemModel.problem_id == problem_id).first()
    if db_problem:
        db_problem.judge_mode = "spj"
        db_problem.spj_code = code
        db_problem.spj_language_id = language_id
        db.commit()
        db.refresh(db_problem)
        return db_problem
    return None

def delete_spj(db:Session, problem_id:str):
    """删除spj"""
    db_problem = db.query(ProblemModel).filter(ProblemModel.problem_id == problem_id).first()
    if db_problem:
        db_problem.judge_mode = "standard"
        db_problem.spj_code = None
        db_problem.spj_language_id = None
        db.commit()
        db.refresh(db_problem)
        return db_problem
    return None