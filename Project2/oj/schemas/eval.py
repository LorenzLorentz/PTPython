from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Eval(BaseModel):
    submission_id:int = Field(..., description="评测id")
    status:str = Field(..., description="评测状态")
    score:int = Field(..., description="得分")
    time:float = Field(..., description="用时")
    memory:int = Field(..., description="内存占用")
    stderr:str = Field(..., description="错误信息")
    action:str = Field(..., description="行为")
    date:datetime = Field(..., description="时间")