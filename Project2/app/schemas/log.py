from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from fastapi import Query
from datetime import datetime

"""Base"""
class LogBase(BaseModel):
    user_id:int = Field(..., description="用户id")
    problem_id:str = Field(..., description="题目id")
    action:str = Field(..., description="行为")
    time:datetime = Field(datetime.today(), description="时间")
    status:int = Field(200, description="状态码")

    model_config = ConfigDict(from_attributes=True)

"""Response"""
class LogResponse(LogBase):
    problem_id:Optional[str] = Field("", description="题目id")

"""Params"""
class LogQueryParams(BaseModel):
    user_id:Optional[int] = Query(None, description="用户id")
    problem_id:Optional[str] = Query(None, description="题目id")
    page:int = Query(0, description="页码")
    page_size:int = Query(10, description="每页数量")