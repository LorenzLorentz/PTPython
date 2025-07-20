from typing import List, Optional, Any
from pydantic import BaseModel, Field, model_validator

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

class LanguageInfoListResponse(BaseModel):
    name: List[str]

    @model_validator(mode='before')
    @classmethod
    def organize_data(cls, values: Any) -> Any:
        if isinstance(values, list):
            language_names = [lang.name for lang in values]
            return {"name": language_names}
        return values

"""Payload"""
class LanguageAddPayload(LanguageBase):
    pass