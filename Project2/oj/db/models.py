from sqlalchemy import Column, Integer, String, ForeignKey, Float, Time, JSON
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
    samples = Column(JSON)
    constraints = Column(String)
    testcases = Column(JSON)
    
    hint = Column(String)
    source = Column(String)
    tags = Column(JSON)
    time_limit = Column(String)
    memory_limit = Column(String)
    author = Column(String)
    difficulty = Column(String)

    evals = relationship("EvalModel", back_populates="problem")

class LanguageModel(Base):
    name = Column(String)
    file_ext = Column(String)
    compile_cmd = Column(String)
    run_cmd = Column(String)
    source_template = Column(String)
    time_limit = Column(Float)
    memory_limit = Column(Integer)

class SubmissionModel(Base):
    __tablename__ = "evals"

    language = Column(LanguageModel)
    code = Column(String)
    
    submission_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(String)
    score = Column(Integer)
    counts = Column(Integer)
    time = Column(Float)
    memory = Column(Integer)

    testcases = Column(JSON)

    problem_id = Column(String, ForeignKey("problems.problem_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))

    user = relationship("UserModel", back_populates="evals")
    problem = relationship("ProblemModel", back_populates="evals")

class LogModel(Base):
    user_id = Column(Integer)
    problem_id = Column(String)
    action = Column(String)
    time = Column(Time)