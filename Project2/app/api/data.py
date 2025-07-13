from fastapi import APIRouter, Depends, Request, UploadFile, File
from typing import List
import json
import pydantic

from app import db
from app.db.database import get_db
from app.api.utils.permission import check_admin
from app.api.utils.exception import APIException
from app.schemas.response import ResponseModel
from app.schemas.data import DataBase

reset_router = APIRouter()
@reset_router.post("/", response_model=ResponseModel[None])
async def reset(request:Request, db_session=Depends(get_db)):
    """系统重置"""
    if not check_admin(request=request, db_session=db_session):
        raise APIException(status_code=403, msg="权限不足")
    try:
        db.db_data.reset(db=db_session)
        return {"msg":"system reset successfully", "data":None}
    except Exception as e:
        raise APIException(status_code=500, msg="服务器异常")

export_router = APIRouter()
@export_router.get("/", response_model=ResponseModel[DataBase])
async def data_export(request:Request, db_session=Depends(get_db)):
    """数据导出"""
    if not check_admin(request=request, db_session=db_session):
        raise APIException(status_code=403, msg="用户无权限")

    try:
        db_data = db.db_data.get_data(db=db_session)
        return {"msg":"success", "data":db_data}
    except Exception as e:
        raise APIException(status_code=500, msg="服务器异常")

import_router = APIRouter()
@import_router.post("/", response_model=ResponseModel[None])
async def data_import(request:Request, file:UploadFile=File(...), db_session=Depends(get_db)):
    """数据导入"""
    if not check_admin(request=request, db_session=db_session):
        raise APIException(status_code=403, msg="用户无权限")

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
        validated_data = DataBase.model_validate(raw_data)
    except pydantic.ValidationError as e:
        raise APIException(status_code=400, msg="参数错误")

    try:
        db.db_data.set_data(db=db_session, data=validated_data)
        return {"msg": "import success", "data": None}
    except Exception as e:
        raise APIException(status_code=500, msg="服务器异常")