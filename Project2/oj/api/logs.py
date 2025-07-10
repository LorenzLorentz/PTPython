from fastapi import APIRouter, Depends, HTTPException, Request, Path
from typing import List, Annotated

from oj import db
from oj.db.database import get_db
from oj.schemas.log import Log, LogQueryPayload
from oj.schemas.response import ResponseModel
from oj.api.utils.permission import check_admin

router = APIRouter()

@router.get("/access", response_model=ResponseModel[Log])
async def get_access_log_list(request:Request, payload:LogQueryPayload, db_session=Depends(get_db)):
    """日志访问审计"""
    if not check_admin(request=request, db_session=db_session):
        raise HTTPException(status_code=403, detail="用户无权限")
    
    db_log_list = db.db_log.get_log_list(
        db=db_session, user_id=payload.user_id, problem_id=payload.problem_id,
        offset=payload.page*payload.page_size, limit=payload.page_size,
    )

    return {"msg": "success", "data": db_log_list}