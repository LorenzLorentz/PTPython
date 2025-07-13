from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.user import UserBase
from app.schemas.problem import ProblemBase
from app.schemas.submission import SubmissionBase, TestCaseResult

"""Submission"""
class SubmissionForData(SubmissionBase):
    status:Optional[str] = Field(None, exclude=True)
    time:Optional[float] = Field(None, exclude=True)
    memory:Optional[int] = Field(None, exclude=True)

class TestCaseResultImport(TestCaseResult):
    id:int = Field(..., validation_alias="id", description="测试点id")

class SubmissionImport(SubmissionForData):
    submission_id:int = Field(..., serialization_alias="id", description="评测id")
    language_name:str = Field(..., validation_alias="language", description="语言")
    test_case_results:List[TestCaseResultImport] = Field(..., validation_alias="details", description="各测试点评测状态")

class SubmissionExport(SubmissionForData):
    submission_id:int = Field(..., validation_alias="id", description="评测id")
    language_name:str = Field(..., serialization_alias="language", description="语言")
    test_case_results:List[TestCaseResult] = Field(..., serialization_alias="details", description="各测试点评测状态")

"""Import"""
class UserImport(UserBase):
    hashed_password:str = Field("", validation_alias="password", description="密码")

class ProblemImport(ProblemBase):
    problem_id:str = Field(..., validation_alias="id", description="题目唯一标识")

class DataImport(BaseModel):
    users:List[UserImport] = Field(..., description="用户")
    problems:List[ProblemImport] = Field(..., description="题目")
    submissions:List[SubmissionImport] = Field(..., description="提交")

"""Export"""
class UserExport(UserBase):
    user_id:int = Field(..., validation_alias="id", description="用户id")
    hashed_password:str = Field("", serialization_alias="password", description="密码")

class ProblemExport(ProblemBase):
    problem_id:str = Field(..., serialization_alias="id", description="题目唯一标识")

class DataExport(BaseModel):
    users:List[UserExport] = Field(..., description="用户")
    problems:List[ProblemExport] = Field(..., description="题目")
    submissions:List[SubmissionExport] = Field(..., description="提交")