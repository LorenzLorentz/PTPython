from fastapi import APIRouter, Depends, Request, Path
from typing import List, Annotated

from app import db
from app.db.database import get_db
from app.schemas.language import LanguageInfo, LanguageAddPayload
from app.schemas.response import ResponseModel
from app.api.utils.permission import check_admin
from app.api.utils.exception import APIException

router = APIRouter()

@router.post("/", response_model=ResponseModel[LanguageInfo])
async def add_language(request:Request, payload:LanguageAddPayload, db_session=Depends(get_db)):
    """动态注册新语言"""
    if not check_admin(request=request, db_session=db_session):
        raise APIException(status_code=403, msg="用户无权限")

    db_language = db.db_language.add_language(db=db_session, language=payload)
    return {"msg": "language registered", "data": db_language}

@router.get("/", response_model=ResponseModel[LanguageInfo])
async def get_language_list(db_session=Depends(get_db)):
    """查询支持语言列表"""
    return db.db_language.get_language_list(db=db_session)