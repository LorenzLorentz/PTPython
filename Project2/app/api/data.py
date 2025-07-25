from fastapi import APIRouter, Depends, Request, UploadFile, File
from typing import List
from sqlalchemy.orm import Session
import json
import pydantic

from app import db
from app.db.database import get_db
from app.db.models import UserModel
from app.api.utils.permission import require_admin
from app.api.utils.exception import APIException
from app.schemas.response import ResponseModel
from app.schemas.data import DataImport, DataExport

reset_router = APIRouter()
@reset_router.post("/", response_model=ResponseModel[None])
async def reset(request:Request, db_admin:UserModel=Depends(require_admin)):
    """
    系统重置
    参数: 无
    权限: 管理员
    """
    request.session.pop("user_id")

    try:
        db.db_data.reset()
        return {"msg":"system reset successfully", "data":None}
    except Exception as e:
        raise APIException(status_code=500, msg="服务器异常")

export_router = APIRouter()
@export_router.get("/", response_model=ResponseModel[DataExport])
async def data_export(db_admin:UserModel=Depends(require_admin), db_session:Session=Depends(get_db)):
    """
    数据导出
    参数: 无
    权限: 管理员
    """
    try:
        db_data = db.db_data.get_data(db=db_session)
        return {"msg":"success", "data":db_data}
    except Exception as e:
        raise APIException(status_code=500, msg="服务器异常")

import_router = APIRouter()
@import_router.post("/", response_model=ResponseModel[None])
async def data_import(file:UploadFile=File(...), db_admin:UserModel=Depends(require_admin), db_session=Depends(get_db)):
    """
    数据导入
    参数: file (文件)
    权限: 管理员
    """
    if not file.filename.endswith('.json'):
        raise APIException(status_code=400, msg="只支持.json文件")

    try:
        content = await file.read()
        decoded_content = content.decode('utf-8')
        raw_data = json.loads(decoded_content)
    except UnicodeDecodeError:
        raise APIException(status_code=400, msg="编码错误")
    except json.JSONDecodeError:
        raise APIException(status_code=400, msg="格式无效, 无法解析")

    try:
        validated_data = DataImport.model_validate(raw_data)
    except pydantic.ValidationError as e:
        raise APIException(status_code=400, msg="参数错误")

    try:
        db.db_data.set_data(db=db_session, data=validated_data)
        return {"code": 200, "msg": "import success", "data": None}
    except Exception as e:
        raise APIException(status_code=500, msg="服务器异常")