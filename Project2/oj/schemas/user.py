from typing import List, Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    user_id:int = Field(..., description="用户id")
    username:str = Field(..., description="用户名")
    password:str = Field(..., description="密码")
    role:str = Field(..., description="权限")

class UserBrief(BaseModel):
    user_id:int = Field(..., description="用户id")
    username:str = Field(..., description="用户名")

class UserInfo(BaseModel):
    user_id:int = Field(..., description="用户id")
    username:str = Field(..., description="用户名")
    role:str = Field(..., description="权限")

class UserRole(BaseModel):
    user_id:int = Field(..., description="用户id")
    role:str = Field(..., description="权限")

class UserID(BaseModel):
    user_id:int = Field(..., description="用户id")

class UserList(BaseModel):
    total:int = Field(..., description="总数")
    users:List[UserInfo] = Field(..., description="用户列表")

"""Payload"""
class UserAddPayload(BaseModel):
    username:str = Field(..., description="用户名")
    password:str = Field(..., description="密码")

class UserRolePayload(BaseModel):
    role:str = Field(..., description="新权限")

class UserQueryPayload(BaseModel):
    username:Optional[str] = Field(None, description="用户名")
    role:Optional[str] = Field(None, description="权限")
    page:Optional[int] = Field(0, description="页码")
    page_size:Optional[int] = Field(10, description="每页大小")