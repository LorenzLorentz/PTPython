from sqlalchemy.orm import Session
from app.db.models import ProblemModel, CaseModel, SampleModel
from app.schemas.problem import ProblemAddPayload

def get_problem(db:Session, problem_id:str):
    return db.query(ProblemModel).filter(ProblemModel.problem_id == problem_id).first()

def get_problem_by_id(db:Session, _problem_id:int):
    return db.query(ProblemModel).filter(ProblemModel.id == _problem_id).first()

def get_problem_list(db:Session):
    return db.query(ProblemModel).all()

def add_problem(db:Session, problem:ProblemAddPayload):
    problem_data = problem.model_dump()
    testcases_data = problem_data.pop("testcases", [])
    samples_data = problem_data.pop("samples", [])
    
    db_problem = ProblemModel(**problem_data)
    db_problem.testcases = [CaseModel(**case) for case in testcases_data]
    db_problem.samples = [SampleModel(**sample) for sample in samples_data]
    
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem

def delete_problem(db:Session, problem_id:str):
    db_problem = db.query(ProblemModel).filter(ProblemModel.problem_id == problem_id).first()
    if db_problem:
        db.delete(db_problem)
        db.commit()
        return db_problem
    return None

def set_problem_log_visibility(db:Session, problem_id:str, log_visibility:bool):
    db_problem = db.query(ProblemModel).filter(ProblemModel.problem_id == problem_id).first()
    if db_problem:
        db_problem.log_visibility = log_visibility
        db.commit()
        db.refresh(db_problem)
        return db_problem
    return None