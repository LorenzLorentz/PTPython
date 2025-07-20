from fastapi import APIRouter, Depends, Request, Path
from typing import List, Annotated
from sqlalchemy.orm import Session

from app import db
from app.db.database import get_db
from app.db.models import UserModel
from app.schemas.log import LogResponse, LogQueryParams
from app.schemas.response import ResponseModel
from app.api.utils.permission import require_admin
from app.api.utils.exception import APIException

router = APIRouter()

@router.get("/access/", response_model=ResponseModel[List[LogResponse]])
async def get_access_log_list(payload:LogQueryParams=Depends(), user_admin:UserModel=Depends(require_admin),db_session:Session=Depends(get_db)):
    """
    日志访问审计
    参数: user_id (str, 可选): 按用户筛选, problem_id (str, 可选): 按题目筛选, page (int, 可选): 页码, page_size (int, 可选): 每页数量
    权限: 管理员
    """
    db_log_list = db.db_log.get_log_list(
        db=db_session, user_id=payload.user_id, problem_id=payload.problem_id,
        offset=payload.page*payload.page_size, limit=payload.page_size,
    )

    return {"msg": "success", "data": db_log_list}