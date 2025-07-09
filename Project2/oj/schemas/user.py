from typing import List, Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    user_id:int = Field(..., description="用户id")
    username:str = Field(..., description="用户名")
    password:str = Field(..., description="密码")
    role:str = Field(..., description="权限")

class UserAdd(BaseModel):
    username:str = Field(..., description="用户名")
    password:str = Field(..., description="密码")

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

class UserQuery(BaseModel):
    username:Optional[str] = Field(None, description="用户名")
    role:Optional[str] = Field(None, description="权限")
    page:Optional[int] = Field(None, description="页码")
    page_size:Optional[int] = Field(None, description="每页大小")

class UserList(BaseModel):
    total:int = Field(..., description="总数")
    users:List[User] = Field(..., description="用户列表")