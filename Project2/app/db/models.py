from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, JSON, Boolean, func
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.ext.hybrid import hybrid_property

class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    join_time = Column(DateTime, server_default=func.now(), nullable=False)
    submit_count = Column(Integer, server_default='0', nullable=False)
    resolve_count = Column(Integer, server_default='0', nullable=False)

    submissions = relationship("SubmissionModel", back_populates="user")
    logs = relationship("LogModel", back_populates="user")

class ProblemModel(Base):
    __tablename__ = "problems"

    _id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    problem_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    input_description = Column(String, nullable=False)
    output_description = Column(String, nullable=False)
    samples = Column(JSON, nullable=False)
    constraints = Column(String, nullable=False)
    testcases = Column(JSON, nullable=False)
    
    hint = Column(String, nullable=True)
    source = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    time_limit = Column(String, nullable=True)
    memory_limit = Column(String, nullable=True)
    author = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    log_visibility = Column(Boolean, nullable=False)

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
    time = Column(DateTime)

    user_id = Column(Integer, ForeignKey("users.user_id"))
    problem_id = Column(String, ForeignKey("problems.problem_id"))

    user = relationship("UserModel", back_populates="logs")
    problem = relationship("ProblemModel", back_populates="logs")