from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from fastapi import Query

"""Base"""
class UserBase(BaseModel):
    user_id:int = Field(..., validation_alias="id", description="用户id")
    username:str = Field(..., description="用户名")
    hashed_password:str = Field(..., description="密码")
    role:str = Field(..., description="权限")
    join_time:datetime = Field(..., description="加入时间")
    submit_count:int = Field(..., description="提交次数")
    resolve_count:int = Field(..., description="解决问题数")

    model_config = ConfigDict(from_attributes=True)

"""Response"""
class UserRoleResponse(BaseModel):
    user_id:int = Field(..., validation_alias="id", description="用户id")
    role:str = Field(..., description="权限")

    model_config = ConfigDict(from_attributes=True)

class UserIDResponse(BaseModel):
    user_id:int = Field(..., validation_alias="id", description="用户id")
    
    model_config = ConfigDict(from_attributes=True)

class UserAdminResponse(BaseModel):
    user_id:int = Field(..., validation_alias="id", description="用户id")
    username:str = Field(..., description="用户名")
    
    model_config = ConfigDict(from_attributes=True)

class UserBriefResponse(BaseModel):
    user_id:int = Field(..., validation_alias="id", description="用户id")
    username:str = Field(..., description="用户名")
    role:str = Field(..., description="权限")
    
    model_config = ConfigDict(from_attributes=True)

class UserInfoResponse(BaseModel):
    user_id:int = Field(..., validation_alias="id", description="用户id")
    username:str = Field(..., description="用户名")
    join_time:datetime = Field(..., description="加入时间")
    role:str = Field(..., description="权限")
    submit_count:int = Field(..., description="提交次数")
    resolve_count:int = Field(..., description="解决问题数")

    model_config = ConfigDict(from_attributes=True)

class UserListResponse(BaseModel):
    total:int = Field(..., description="总数")
    users:List[UserInfoResponse] = Field(..., description="用户列表")

    model_config = ConfigDict(from_attributes=True)

"""Payload"""
class UserAddPayload(BaseModel):
    username:str = Field(..., description="用户名")
    password:str = Field(..., description="密码")

class UserRolePayload(BaseModel):
    role:str = Field(..., description="新权限")

"""Params"""
class UserQueryParams:
    def __init__(
        self,
        page:int = Query(1, description="页码", ge=1),
        page_size:int = Query(10, description="每页大小", gt=0)
    ):
        self.page = page
        self.page_size = page_size