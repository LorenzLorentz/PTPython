from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

"""Base"""
class LogBase(BaseModel):
    user_id:int = Field(..., description="用户id")
    problem_id:str = Field(..., description="题目id")
    action:str = Field(..., description="行为")
    time:datetime = Field(datetime.today(), description="时间")

    model_config = ConfigDict(from_attributes=True)

"""Response"""
class LogResponse(LogBase):
    pass

"""Payload"""
class LogQueryPayload(BaseModel):
    user_id:int = Field(..., description="用户id")
    problem_id:str = Field(..., description="题目id")
    page:Optional[int] = Field(0, description="页码")
    page_size:Optional[int] = Field(10, description="每页数量")