from sqlalchemy.orm import Session
from oj.db.models import Problem
from oj.schemas.problem import ProblemAdd

def get_problem(db:Session, problem_id:str):
    return db.query(Problem).filter(Problem.problem_id == problem_id).first()

def get_problem_list(db:Session, offset:int, limit:int):
    return db.query(Problem).offset(offset).limit(limit).all()

def add_problem(db:Session, problem:ProblemAdd):
    db_problem = Problem()
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem

def delete_problem(db:Session, problem_id:str):
    db_problem = db.query(Problem).filter(Problem.problem_id == problem_id).first()
    if db_problem:
        db.delete(db_problem)
        db.commit()
        return db_problem
    return None