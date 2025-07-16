from fastapi import APIRouter, Depends, Request, Path
from typing import List, Annotated
from sqlalchemy.orm import Session

from app import db
from app.db.database import get_db
from app.db.models import UserModel
from app.schemas.language import LanguageInfoResponse, LanguageAddPayload, LanguageInfoListResponse
from app.schemas.response import ResponseModel
from app.api.utils.permission import require_login
from app.api.utils.exception import APIException
from app.judger.secure import check_cmd_available

router = APIRouter()

@router.post("/", response_model=ResponseModel[LanguageInfoResponse])
async def add_language(payload:LanguageAddPayload, user_login:UserModel=Depends(require_login), db_session:Session=Depends(get_db)):
    """动态注册新语言"""
    exist = db.db_language.get_language_by_name(db=db_session, name=payload.name)
    if exist:
        return {"msg": "language registered", "data": exist}
    
    if not check_cmd_available(payload.compile_cmd) or not check_cmd_available(payload.run_cmd):
        raise APIException(status_code=400, msg="非法命令!!!")

    db_language = db.db_language.add_language(db=db_session, language=payload)
    return {"msg": "language registered", "data": db_language}

@router.get("/", response_model=ResponseModel[LanguageInfoListResponse])
async def get_language_list(db_session:Session=Depends(get_db)):
    """查询支持语言列表"""
    return {"msg": "success", "data": db.db_language.get_language_list(db=db_session)}