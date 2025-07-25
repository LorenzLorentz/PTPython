import enum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, JSON, Boolean, Enum, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.db.database import Base

"""Enums"""
class StatusCategory(enum.Enum):
    """单个评测点评测状态"""
    AC = "AC"
    WA = "WA"
    RE = "RE"
    TLE = "TLE"
    MLE = "MLE"
    CE = "CE"
    JUDGING = "judging"
    PENDING = "pending"
    COMPILING = "compiling"
    UNK = "UNK"

class SubmissionStatusCategory(enum.Enum):
    """题目状态"""
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"

"""Models"""
class UserModel(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), index=True, nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user", index=True, nullable=False)
    join_time = Column(DateTime, server_default=func.now(), nullable=False)
    submit_count = Column(Integer, default=0, nullable=False)
    resolve_count = Column(Integer, default=0, nullable=False)

    # Relationships
    submissions = relationship("SubmissionModel", back_populates="user")
    logs = relationship("LogModel", back_populates="user")

class SampleModel(Base):
    """样例模型"""
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)

    # ForeignKey
    _problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), index=True, nullable=False)

    # Relationships
    problem = relationship("ProblemModel", back_populates="samples")

class CaseModel(Base):
    """测试点模型"""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)

    # ForeignKey
    _problem_id = Column(Integer, ForeignKey("problems.id", ondelete="CASCADE"), index=True, nullable=False)

    # Relationships
    problem = relationship("ProblemModel", back_populates="testcases")
    test_case_results = relationship("TestCaseResultModel", back_populates="case")

class ProblemModel(Base):
    """题目模型"""
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    problem_id = Column(String(255), index=True, nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    input_description = Column(Text, nullable=False)
    output_description = Column(Text, nullable=False)
    constraints = Column(Text, nullable=False)
    
    hint = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)
    time_limit = Column(Float, default=1.0, nullable=False)
    memory_limit = Column(Integer, default=256, nullable=False)
    author = Column(String(255), nullable=True)
    difficulty = Column(String(50), nullable=True)
    log_visibility = Column(Boolean, default=False, nullable=False)

    # SPJ
    judge_mode = Column(String(50), default="standard", nullable=False)
    spj_code = Column(Text, nullable=True)
    spj_language_id = Column(Integer, ForeignKey("languages.id"), nullable=True)
    spj_language = relationship("LanguageModel", back_populates="problem")

    # Relationships
    submissions = relationship("SubmissionModel", back_populates="problem")
    logs = relationship("LogModel", back_populates="problem")
    samples = relationship("SampleModel", back_populates="problem", cascade="all, delete-orphan")
    testcases = relationship("CaseModel", back_populates="problem", cascade="all, delete-orphan")
    plagiarism_tasks = relationship("PlagiarismTaskModel", back_populates="problem")

    @hybrid_property
    def spj_language_name(self) -> str | None:
        if self.spj_language:
            return self.spj_language.name
        return None

class LanguageModel(Base):
    """语言模型"""
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False, unique=True)
    file_ext = Column(String(50), nullable=False)
    compile_cmd = Column(Text, nullable=True)
    run_cmd = Column(Text, nullable=False)
    source_template = Column(Text, nullable=True)
    time_limit = Column(Float, default=0.0, nullable=False)
    memory_limit = Column(Integer, default=0, nullable=False)

    # Relationships
    problem = relationship("ProblemModel", back_populates="spj_language")
    submissions = relationship("SubmissionModel", back_populates="language")

class TestCaseResultModel(Base):
    """测试点结果模型"""
    __tablename__ = "test_case_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    test_case_result_id = Column(Integer, nullable=False)
    result = Column(Enum(StatusCategory), default=StatusCategory.PENDING, nullable=False)
    time = Column(Float, default=0.0, nullable=False)
    memory = Column(Integer, default=0, nullable=False)
    output = Column(Text, default="", nullable=False)
    err_msg = Column(Text, default="", nullable=False)

    # ForeignKey
    submission_id = Column(Integer, ForeignKey("submissions.id"), index=True, nullable=False)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)

    # Relationships
    submission = relationship("SubmissionModel", back_populates="test_case_results")
    case = relationship("CaseModel", back_populates="test_case_results")

class SubmissionModel(Base):
    """提交模型"""
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(Text, nullable=False)
    status = Column(Enum(SubmissionStatusCategory), default=SubmissionStatusCategory.PENDING, index=True, nullable=False)
    score = Column(Integer, default=0, nullable=False)
    counts = Column(Integer, default=0, nullable=False)
    time = Column(Float, default=0.0, nullable=False)
    memory = Column(Integer, default=0, nullable=False)
    pdg = Column(JSON, nullable=True)

    # ForeignKey
    _problem_id = Column(Integer, ForeignKey("problems.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=True)

    # RelationShips
    user = relationship("UserModel", back_populates="submissions")
    problem = relationship("ProblemModel", back_populates="submissions")
    language = relationship("LanguageModel", back_populates="submissions")
    test_case_results = relationship("TestCaseResultModel", back_populates="submission", cascade="all, delete-orphan")
    plagiarism_task = relationship("PlagiarismTaskModel", back_populates="submission", uselist=False, cascade="all, delete-orphan")

    @hybrid_property
    def problem_id(self) -> str | None:
        if self.problem:
            return self.problem.problem_id
        return None
    
    @hybrid_property
    def language_name(self) -> str | None:
        if self.language:
            return self.language.name
        return None

class LogModel(Base):
    """题目模型"""
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    action = Column(String(255), nullable=False)
    time = Column(DateTime, server_default=func.now(), nullable=False)
    status = Column(Integer, default=200, nullable=False)

    # ForeignKey
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    _problem_id = Column(Integer, ForeignKey("problems.id"), index=True, nullable=True)

    # RelationShips
    user = relationship("UserModel", back_populates="logs")
    problem = relationship("ProblemModel", back_populates="logs")

    @hybrid_property
    def problem_id(self) -> str | None:
        if self.problem:
            return self.problem.problem_id
        return None
    
class PlagiarismTaskModel(Base):
    """查重任务模型"""
    __tablename__ = "plagiarism_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    threshold = Column(Float, default=0.8, nullable=False)
    result = Column(Boolean, default=False, nullable=False)

    sim_list = Column(JSON, nullable=False, default=list)
    sim_abstract = Column(JSON, nullable=True)
    sim_submission_id_list = Column(JSON, nullable=True)

    # ForeignKey
    _problem_id = Column(Integer, ForeignKey("problems.id"), index=True, nullable=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), index=True, nullable=False)
    
    # RelationShips
    problem = relationship("ProblemModel", back_populates="plagiarism_tasks")
    submission = relationship("SubmissionModel", back_populates="plagiarism_task", foreign_keys=[submission_id])