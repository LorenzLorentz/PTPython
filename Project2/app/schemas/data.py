from typing import List, Optional, Any
from pydantic import BaseModel, Field, model_validator

from app.schemas.user import UserBase
from app.schemas.problem import ProblemBase
from app.schemas.submission import SubmissionBase, TestCaseResultDetail

"""Base"""
class SubmissionForData(SubmissionBase):
    status:str = Field(..., exclude=True)    
    time:Optional[float] = Field(..., exclude=True)
    memory:Optional[int] = Field(..., exclude=True)

    test_case_results:List[TestCaseResultDetail] = Field(..., serialization_alias="status", description="各测试点评测状态")

class DataBase(BaseModel):
    users:List[UserBase] = Field(..., description="用户")
    problems:List[ProblemBase] = Field(..., description="题目")
    submissions:List[SubmissionForData] = Field(..., description="提交")

"""Response"""
class DataResponse(DataBase):
    pass

"""Payload"""
class DataPayload(DataBase):
    pass