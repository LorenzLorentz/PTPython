from typing import List, Optional
from pydantic import BaseModel, Field

class Case(BaseModel):
    input:str
    output:str

    class Config:
        from_attributes = True

class Problem(BaseModel):
    # 必填字段
    problem_id:str = Field(..., description="题目唯一标识")
    title:str = Field(..., description="题目标题")
    description:str = Field(..., description="题目描述")
    input_description:str = Field(..., description="输入格式说明")
    output_description:str = Field(..., description="输出格式说明")
    samples:List[Case] = Field(..., description="样例输入输出")
    constraints:str = Field(..., description="数据范围和限制条件")
    testcases:List[Case] = Field(..., description="测试点")

    # 可选字段
    hint:Optional[str] = Field(None, description="额外提示")
    source:Optional[str] = Field(None, description="题目来源")
    tags:Optional[List[str]] = Field(None, description="题目标签")
    time_limit:float = Field(1.0, description="时间限制(单位:秒)", example=1.0)
    memory_limit:int = Field(256, description="内存限制(单位:MB)", example=256)
    author:Optional[str] = Field(None, description="题目作者")
    difficulty:Optional[str] = Field(None, description="难度等级")
    log_visibility:Optional[bool] = Field(False, description="日志/测例可见性")

    class Config:
        from_attributes = True

class ProblemID(BaseModel):
    problem_id:str = Field(..., alias="id", description="题目唯一标识")
    class Config:
        from_attributes = True

class ProblemBrief(BaseModel):
    problem_id:str = Field(..., alias="id", description="题目唯一标识")
    title:str = Field(..., description="题目标题")

    class Config:
        from_attributes = True

class ProblemLogVisibility(BaseModel):
    problem_id:str = Field(..., description="题目唯一标识")
    public_cases:bool = Field(..., alias="public_cases", description="是否允许所有用户查看测例详情")

"""payload"""
class ProblemAddPayload(Problem):
    pass

class ProblemSetLogVisibilityPayload(BaseModel):
    problem_id:str = Field(..., description="题目唯一标识")
    public_cases:bool = Field(..., description="是否允许所有用户查看测例详情")