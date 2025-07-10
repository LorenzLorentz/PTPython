from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from app.schemas.language import Language
from app.schemas.problem import Case

class TestCase(BaseModel):
    id:int = Field(..., description="测试点id")
    result:str = Field(..., description="测试点结果")
    time:float = Field(..., description="测试点用时")
    memory:int = Field(..., description="测试点内存占用")

class TestCaseDetail(TestCase):
    case:Case = Field(..., description="测试用例")
    output:str = Field(..., description="预期输出")
    err_msg:str = Field(..., description="错误信息")

class Submission(BaseModel):
    problem_id:str = Field(..., description="题目编号")
    language:Language = Field(..., description="语言")
    code:str = Field(..., description="用户代码内容")
    user_id:int = Field(..., decimal_places="用户id")
    submission_id:int = Field(..., description="评测id")
    
    status:str = Field(..., description="评测状态")    
    score:Optional[int] = Field(..., description="测试点分数")
    counts:Optional[int] = Field(..., description="总分数")
    time:Optional[float] = Field(..., description="用时")
    memory:Optional[int] = Field(..., description="内存占用")

    test_cases:List[TestCaseDetail] = Field(..., description="各测试点评测状态")

class SubmissionError(BaseModel):
    submission_id:int = Field(..., description="评测id")
    status:str = Field(..., description="评测状态")

    model_config = ConfigDict(from_attributes=True)

class SubmissionStatus(BaseModel):
    submission_id:int = Field(..., description="评测id")
    status:str = Field(..., description="评测状态")

    model_config = ConfigDict(from_attributes=True)

class SubmissionResult(BaseModel):
    score:int = Field(..., description="得分")
    counts:int = Field(..., description="总分数")

    model_config = ConfigDict(from_attributes=True)

class SubmissionInfo(BaseModel):
    submission_id:int = Field(..., description="评测id")
    status:str = Field(..., description="评测状态")
    score:int = Field(..., description="得分")
    counts:int = Field(..., description="总分数")

    model_config = ConfigDict(from_attributes=True)

class SubmissionList(BaseModel):
    total:int = Field(..., description="总数")
    submissions:List[SubmissionInfo] = Field(..., description="评测列表")

    model_config = ConfigDict(from_attributes=True)

class SubmissionLog(BaseModel):
    test_cases:List[TestCase] = Field(..., alias="status", description="各测试点评测状态")
    score:Optional[int] = Field(..., description="测试点分数")
    counts:Optional[int] = Field(..., description="总分数")

    model_config = ConfigDict(from_attributes=True)

class SubmissionLogDetail(BaseModel):
    test_cases:List[TestCaseDetail] = Field(..., alias="status", description="各测试点详细评测状态")
    score:Optional[int] = Field(..., description="测试点分数")
    counts:Optional[int] = Field(..., description="总分数")

    model_config = ConfigDict(from_attributes=True)

"""payload"""
class SubmissionAddPayload(BaseModel):
    problem_id:str = Field(..., description="题目编号")
    language:Language = Field(..., description="语言")
    code:str = Field(..., description="用户代码内容")

class SubmissionQueryPayload(BaseModel):
    user_id:Optional[int] = Field(None, description="用户id")
    problem_id:Optional[str] = Field(None, description="题目id")
    status:Optional[str] = Field(None, description="评测状态")
    page:int = Field(..., description="页码")
    page_size:int = Field(..., description="每页大小")