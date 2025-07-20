from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, computed_field

"""Base"""
class Case(BaseModel):
    input:str
    output:str

    model_config = ConfigDict(from_attributes=True)

class ProblemBase(BaseModel):
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
    hint:str = Field("", description="额外提示")
    source:str = Field("", description="题目来源")
    tags:List[str] = Field([], description="题目标签")
    time_limit:float = Field(1.0, description="时间限制(单位:秒)")
    memory_limit:int = Field(256, description="内存限制(单位:MB)")
    author:str = Field("", description="题目作者")
    difficulty:str = Field("", description="难度等级")
    log_visibility:bool = Field(False, description="日志/测例可见性")
    
    # 特殊评测
    judge_mode:str = Field("standard", description="评测策略")
    spj_code:Optional[str] = Field(None, description="SPJ脚本代码")
    spj_language_name:Optional[str] = Field(None, description="SPJ脚本语言")

    model_config = ConfigDict(from_attributes=True)

"""Response"""
class ProblemInfoResponse(ProblemBase):
    problem_id:str = Field(..., serialization_alias="id", description="题目唯一标识")

    model_config = ConfigDict(from_attributes=True)

class ProblemIDResponse(BaseModel):
    problem_id:str = Field(..., serialization_alias="id", description="题目唯一标识")
    
    model_config = ConfigDict(from_attributes=True)

class ProblemBriefResponse(BaseModel):
    problem_id:str = Field(..., serialization_alias="id", description="题目唯一标识")
    title:str = Field(..., description="题目标题")

    model_config = ConfigDict(from_attributes=True)

class ProblemLogVisibilityResponse(BaseModel):
    problem_id:str = Field(..., description="题目唯一标识")
    log_visibility:bool = Field(..., serialization_alias="public_cases", description="是否允许所有用户查看测例详情")

    model_config = ConfigDict(from_attributes=True)

"""Payload"""
class ProblemAddPayload(ProblemBase):
    problem_id:str = Field(..., validation_alias="id", description="题目唯一标识")

class ProblemSetLogVisibilityPayload(BaseModel):
    public_cases:bool = Field(..., description="是否允许所有用户查看测例详情")

class ProblemSetJudgeModePayload(BaseModel):
    judge_mode:str = Field("standard", description="评测策略")