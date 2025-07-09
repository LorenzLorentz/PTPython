from sqlalchemy import Column, Integer, String, ForeignKey, Float, Time
from sqlalchemy.orm import relationship
from oj.db.database import Base

class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String)
    password = Column(String)
    role = Column(String)
    join_time = Column(Time)
    submit_count = Column(Integer)
    resolve_count = Column(Integer)

    evals = relationship("EvalModel", back_populates="user")

class ProblemModel(Base):
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

    evals = relationship("EvalModel", back_populates="problem")

class EvalModel(Base):
    __tablename__ = "evals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    submission_id = Column(Integer)
    status = Column(String)
    score = Column(Integer)
    time = Column(Float)
    memory = Column(Integer)
    stderr = Column(String)
    action = Column(String)
    time = Column(Time)

    problem_id = Column(String, ForeignKey("problems.problem_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))

    user = relationship("UserModel", back_populates="evals")
    problem = relationship("ProblemModel", back_populates="evals")