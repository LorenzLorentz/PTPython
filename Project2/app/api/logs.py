from fastapi import APIRouter, Depends, Request, Path
from typing import List, Annotated

from app import db
from app.db.database import get_db
from app.schemas.log import LogResponse, LogQueryParams
from app.schemas.response import ResponseModel
from app.api.utils.permission import check_admin, check_login
from app.api.utils.exception import APIException

router = APIRouter()

@router.get("/access/", response_model=ResponseModel[List[LogResponse]])
async def get_access_log_list(request:Request, payload:LogQueryParams=Depends(), db_session=Depends(get_db)):
    """日志访问审计"""
    if not check_login(request=request, db_session=db_session):
        raise APIException(status_code=401, msg="用户未登录")
    
    if not check_admin(request=request, db_session=db_session):
        raise APIException(status_code=403, msg="用户无权限")
    
    db_log_list = db.db_log.get_log_list(
        db=db_session, user_id=payload.user_id, problem_id=payload.problem_id,
        offset=payload.page*payload.page_size, limit=payload.page_size,
    )

    return {"msg": "success", "data": db_log_list}