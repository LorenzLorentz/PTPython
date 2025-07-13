from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, computed_field
from datetime import datetime
from fastapi import APIRouter, Depends, Query

from app.schemas.problem import Case

"""Base"""
class TestCaseResult(BaseModel):
    id:int = Field(..., validation_alias="test_case_result_id", description="测试点id")
    result:str = Field(..., description="测试点结果")
    time:float = Field(..., description="测试点用时")
    memory:int = Field(..., description="测试点内存占用")
    
    model_config = ConfigDict(from_attributes=True)

class TestCaseResultDetail(TestCaseResult):
    case:Case = Field(..., description="测试用例")
    output:str = Field(..., description="预期输出")
    err_msg:str = Field(..., description="错误信息")

    model_config = ConfigDict(from_attributes=True)

class SubmissionBase(BaseModel):
    submission_id:int = Field(..., description="评测id")
    user_id:int = Field(..., description="用户id")
    problem_id:str = Field(..., description="题目编号")
    language_name:str = Field(..., description="语言")
    
    code:str = Field(..., description="用户代码内容")
    status:str = Field(..., description="评测状态")    
    score:int = Field(0, description="测试点分数")
    counts:int = Field(0, description="总分数")
    time:Optional[float] = Field(..., description="用时")
    memory:Optional[int] = Field(..., description="内存占用")

    test_case_results:List[TestCaseResultDetail] = Field(..., description="各测试点评测状态")

"""Response"""
class SubmissionErrorResponse(BaseModel):
    submission_id:int = Field(..., validation_alias="id", description="评测id")
    status:str = Field(..., description="评测状态")

    model_config = ConfigDict(from_attributes=True)

class SubmissionStatusResponse(BaseModel):
    submission_id:int = Field(..., validation_alias="id", description="评测id")
    status:str = Field(..., description="评测状态")

    model_config = ConfigDict(from_attributes=True)

class SubmissionResultResponse(BaseModel):
    score:int = Field(..., description="得分")
    counts:int = Field(..., description="总分数")

    model_config = ConfigDict(from_attributes=True)

class SubmissionInfoResponse(BaseModel):
    submission_id:int = Field(..., validation_alias="id", description="评测id")
    status:str = Field(..., description="评测状态")
    score:int = Field(..., description="得分")
    counts:int = Field(..., description="总分数")

    model_config = ConfigDict(from_attributes=True)

class SubmissionListResponse(BaseModel):
    total:int = Field(..., description="总数")
    submissions:List[SubmissionInfoResponse] = Field(..., description="评测列表")

    model_config = ConfigDict(from_attributes=True)

class SubmissionLogResponse(BaseModel):
    test_case_results:List[TestCaseResult] = Field(..., validation_alias='test_case_results', serialization_alias='details', description="各测试点评测状态")
    score:Optional[int] = Field(..., description="测试点分数")
    counts:Optional[int] = Field(..., description="总分数")

    model_config = ConfigDict(from_attributes=True)

class SubmissionLogDetailResponse(BaseModel):
    test_cases:List[TestCaseResultDetail] = Field(..., validation_alias='test_case_results', serialization_alias='details', description="各测试点详细评测状态")
    score:Optional[int] = Field(..., description="测试点分数")
    counts:Optional[int] = Field(..., description="总分数")

    model_config = ConfigDict(from_attributes=True)

"""Payload"""
class SubmissionAddPayload(BaseModel):
    problem_id:str = Field(..., description="题目编号")
    language_name:str = Field(..., alias="language", description="语言")
    code:str = Field(..., description="用户代码内容")

"""Params"""
class SubmissionQueryParams(BaseModel):
    user_id:Optional[int] = Field(None, description="用户id")
    problem_id:Optional[str] = Field(None, description="题目id")
    status:Optional[str] = Field(None, description="评测状态")
    page:int = Field(0, description="页码", ge=0)
    page_size:int = Field(10, description="每页大小", gt=0)