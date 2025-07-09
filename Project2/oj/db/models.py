from sqlalchemy import Column, Integer, String, ForeignKey, Float, Time
# from sqlalchemy.orm import relationship
from oj.db.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer)
    username = Column(String)
    password = Column(String)
    role = Column(String)

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(String)
    title = Column(String)
    description = Column(String)
    input_description = Column(String)
    output_description = Column(String)
    samples = Column(String)
    constraints = Column(String)
    testcases = Column(String)
    
    hint = Column(String)
    source = Column(String)
    tags = Column(String)
    time_limit = Column(String)
    memory_limit = Column(String)
    author = Column(String)
    difficulty = Column(String)

class Eval(Base):
    __tablename__ = "evals"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer)
    status = Column(String)
    score = Column(Integer)
    time = Column(Float)
    memory = Column(Integer)
    stderr = Column(String)
    action = Column(String)
    time = Column(Time)

    problem_id = Column(Integer, ForeignKey("problems.problem_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))