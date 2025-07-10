from fastapi import APIRouter, Depends, HTTPException, Request, Path
from typing import List, Annotated

from oj import db
from oj.db.database import get_db
from oj.schemas.language import LanguageInfo, LanguageAddPayload
from oj.schemas.response import ResponseModel
from oj.api.utils.permission import check_admin

router = APIRouter()

@router.post("/", response_model=ResponseModel[LanguageInfo])
async def add_language(request:Request, payload:LanguageAddPayload, db_session=Depends(get_db)):
    """动态注册新语言"""
    if not check_admin(request=request, db_session=db_session):
        raise HTTPException(status_code=403, detail="用户无权限")

    db_language = db.db_language.add_language(db=db_session, language=payload)
    return {"msg": "language registered", "data": db_language}

@router.get("/", response_model=ResponseModel[LanguageInfo])
async def get_language_list(db_session=Depends(get_db)):
    """查询支持语言列表"""
    return db.db_language.get_language_list(db=db_session)