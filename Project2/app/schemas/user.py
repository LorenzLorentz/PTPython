from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from fastapi import Query

class User(BaseModel):
    user_id:int = Field(..., description="用户id")
    username:str = Field(..., description="用户名")
    password:str = Field(..., description="密码")
    role:str = Field(..., description="权限")
    join_time:datetime = Field(..., description="加入时间")
    submit_count:int = Field(..., description="提交次数")
    resolve_count:int = Field(..., description="解决问题数")

    model_config = ConfigDict(from_attributes=True)

"""Response"""
class UserAdmin(BaseModel):
    user_id:int = Field(..., description="用户id")
    username:str = Field(..., description="用户名")
    
    model_config = ConfigDict(from_attributes=True)

class UserBrief(BaseModel):
    user_id:int = Field(..., description="用户id")
    username:str = Field(..., description="用户名")
    role:str = Field(..., description="权限")
    
    model_config = ConfigDict(from_attributes=True)

class UserInfo(BaseModel):
    user_id:int = Field(..., description="用户id")
    username:str = Field(..., description="用户名")
    join_time:datetime = Field(..., description="加入时间")
    role:str = Field(..., description="权限")
    submit_count:int = Field(..., description="提交次数")
    resolve_count:int = Field(..., description="解决问题数")

    model_config = ConfigDict(from_attributes=True)

class UserRole(BaseModel):
    user_id:int = Field(..., description="用户id")
    role:str = Field(..., description="权限")

    model_config = ConfigDict(from_attributes=True)

class UserID(BaseModel):
    user_id:int = Field(..., description="用户id")
    
    model_config = ConfigDict(from_attributes=True)

class UserList(BaseModel):
    total:int = Field(..., description="总数")
    users:List[UserInfo] = Field(..., description="用户列表")

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
        page:Optional[int] = Query(0, description="页码", ge=0),
        page_size:Optional[int] = Query(10, description="每页大小", gt=0)
    ):
        self.page = page
        self.page_size = page_size