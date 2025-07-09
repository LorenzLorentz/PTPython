from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class User(BaseModel):
    user_id:int = Field(..., description="用户id")
    username:str = Field(..., description="用户名")
    password:str = Field(..., description="密码")
    role:str = Field(..., description="权限")
    join_time:datetime = Field(datetime.now(), description="加入时间")
    submit_count:int = Field(0, description="提交次数")
    resolve_count:int = Field(0, description="解决问题数")

    class Config:
        from_attributes = True

class UserBrief(BaseModel):
    user_id:int = Field(..., description="用户id")
    username:str = Field(..., description="用户名")
    
    class Config:
        from_attributes = True

class UserInfo(BaseModel):
    user_id:int = Field(..., description="用户id")
    join_time:datetime = Field(datetime.now(), description="加入时间")
    submit_count:int = Field(0, description="提交次数")
    resolve_count:int = Field(0, description="解决问题数")

    class Config:
        from_attributes = True

class UserRole(BaseModel):
    user_id:int = Field(..., description="用户id")
    role:str = Field(..., description="权限")

    class Config:
        from_attributes = True

class UserID(BaseModel):
    user_id:int = Field(..., description="用户id")
    
    class Config:
        from_attributes = True

class UserList(BaseModel):
    total:int = Field(..., description="总数")
    users:List[UserInfo] = Field(..., description="用户列表")

    class Config:
        from_attributes = True

"""Payload"""
class UserAddPayload(BaseModel):
    username:str = Field(..., description="用户名")
    password:str = Field(..., description="密码")

class UserRolePayload(BaseModel):
    role:str = Field(..., description="新权限")

class UserQueryPayload(BaseModel):
    page:Optional[int] = Field(0, description="页码")
    page_size:Optional[int] = Field(10, description="每页大小")