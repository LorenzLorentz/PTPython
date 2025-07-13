from typing import List, Optional, Any
from pydantic import BaseModel, Field, model_validator

from app.schemas.user import UserBase, UserAddPayload
from app.schemas.problem import ProblemBase
from app.schemas.submission import SubmissionBase, TestCaseResultDetail

class SubmissionForData(SubmissionBase):
    status:str = Field(..., exclude=True)    
    time:Optional[float] = Field(..., exclude=True)
    memory:Optional[int] = Field(..., exclude=True)

    test_case_results:List[TestCaseResultDetail] = Field(..., serialization_alias="status", description="各测试点评测状态")

"""Import"""
class UserImport(UserBase):
    user_id:Optional[int] = Field(None, validation_alias="id", description="用户id")
    username:str = Field(..., description="用户名")
    hashed_password:str = Field(..., validation_alias="password", description="密码")

class DataImport(BaseModel):
    users:List[UserImport] = Field(..., description="用户")
    problems:List[ProblemBase] = Field(..., description="题目")
    submissions:List[SubmissionForData] = Field(..., description="提交")

"""Export"""
class UserExport(UserBase):
    hashed_password:str = Field("", serialization_alias="password", description="密码")

class ProblemExport(ProblemBase):
    problem_id:str = Field(..., validation_alias="problem_id", serialization_alias="id", description="题目唯一标识")

class DataExport(BaseModel):
    users:List[UserExport] = Field(..., description="用户")
    problems:List[ProblemBase] = Field(..., description="题目")
    submissions:List[SubmissionForData] = Field(..., description="提交")