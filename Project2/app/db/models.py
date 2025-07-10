from sqlalchemy import Column, Integer, String, ForeignKey, Float, Time, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.ext.hybrid import hybrid_property

class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String)
    password = Column(String)
    role = Column(String)
    join_time = Column(Time)
    submit_count = Column(Integer)
    resolve_count = Column(Integer)

    submissions = relationship("SubmissionModel", back_populates="user")
    logs = relationship("LogModel", back_populates="user")

class ProblemModel(Base):
    __tablename__ = "problems"

    _id = Column(Integer, primary_key=True, index=True, autoincrement=True)
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
    log_visibility = Column(Boolean)

    submissions = relationship("SubmissionModel", back_populates="problem")
    logs = relationship("LogModel", back_populates="problem")

    @hybrid_property
    def id(self):
        return self.problem_id

class LanguageModel(Base):
    __tablename__ = "languages"

    _id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    file_ext = Column(String)
    compile_cmd = Column(String)
    run_cmd = Column(String)
    source_template = Column(String)
    time_limit = Column(Float)
    memory_limit = Column(Integer)

    submissions = relationship("SubmissionModel", back_populates="language")

class SubmissionModel(Base):
    __tablename__ = "submissions"

    submission_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String)
    status = Column(String)
    score = Column(Integer)
    counts = Column(Integer)
    time = Column(Float)
    memory = Column(Integer)

    testcases = Column(JSON)

    problem_id = Column(String, ForeignKey("problems.problem_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    language_id = Column(Integer, ForeignKey("languages._id"))

    user = relationship("UserModel", back_populates="submissions")
    problem = relationship("ProblemModel", back_populates="submissions")
    language = relationship("LanguageModel", back_populates="submissions")

class LogModel(Base):
    __tablename__ = "logs"

    _id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    action = Column(String)
    time = Column(Time)

    user_id = Column(Integer, ForeignKey("users.user_id"))
    problem_id = Column(String, ForeignKey("problems.problem_id"))

    user = relationship("UserModel", back_populates="logs")
    problem = relationship("ProblemModel", back_populates="logs")