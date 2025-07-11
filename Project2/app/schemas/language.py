from typing import List, Optional
from pydantic import BaseModel, Field

"""Base"""
class LanguageBase(BaseModel):
    name:str = Field(..., description="语言名称")
    file_ext:str = Field(..., description="代码文件拓展名")

    compile_cmd:Optional[str] = Field(None, description="编译命令")
    run_cmd:str = Field(..., description="运行命令")
    source_template:Optional[str] = Field(None, description="代码运行模板")

    time_limit:float = Field(1.0, description="时间限制(默认单位为's')")
    memory_limit:int = Field(256, description="空间限制(默认单位为'MB)")

"""Response"""
class LanguageInfoResponse(BaseModel):
    name:str = Field(..., description="语言名称")
    run_cmd:str = Field(..., description="运行命令")

"""Payload"""
class LanguageAddPayload(LanguageBase):
    pass