from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from fastapi import Query
from datetime import datetime

"""Base"""
class PlagiarismTask(BaseModel):
    task_id:int = Field(..., description="查重任务id")
    problem_id:str = Field(..., description="题目编号")
    submission_id:str = Field(..., description="提交编号")
    
    threshold:float = Field(0.8, description="相似度阈值", le=1)
    result:bool = Field(False, description="查重结果")
    sim_submission_id_list:List[int] = Field([], description="对比对象")
    sim_list:List[float] = Field([], description="相似度评分")
    sim_abstract_list:Optional[List[dict]] = Field(None, description="可视化摘要")

    model_config = ConfigDict(from_attributes=True)

"""Response"""
class PlagiarismTaskIDResponse(BaseModel):
    task_id:int = Field(..., validation_alias="id", description="查重任务id")
    model_config = ConfigDict(from_attributes=True)

class PlagiarismTaskResultResponse(BaseModel):
    task_id:int = Field(..., validation_alias="id", description="查重任务id")
    result:bool = Field(True, description="查重结果")
    model_config = ConfigDict(from_attributes=True)

class PlagiarismTaskReportResponse(BaseModel):
    result:bool = Field(True, validation_alias="id", description="查重结果")
    sim_submission_id_list:List[int] = Field([], description="对比对象")
    sim_list:List[float] = Field([], description="相似度评分")
    sim_abstract:Optional[List[dict]] = Field(None, description="可视化摘要")

"""Payload"""
class PlagiarismTaskLaunchPayload(BaseModel):
    problem_id:str = Field(..., description="题目编号")
    submission_id:str = Field(..., description="提交编号")
    threshold:Optional[float] = Field(0.8, description="相似度阈值", le=1)