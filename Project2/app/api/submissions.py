from fastapi import APIRouter, Depends
from typing import List, Annotated, Union
from sqlalchemy.orm import Session

from app import db
from app.db.database import get_db
from app.db.models import UserModel
from app.schemas.submission import (
    SubmissionResultResponse, SubmissionStatusResponse, SubmissionListResponse, SubmissionLogResponse, SubmissionLogDetailResponse,
    SubmissionAddPayload, SubmissionQueryParams
)
from app.schemas.response import ResponseModel
from app.api.utils.permission import require_admin, require_login, require_notbanned
from app.api.utils.exception import APIException

router = APIRouter()

@router.post("/", response_model=ResponseModel[SubmissionStatusResponse])
async def submit(payload:SubmissionAddPayload, db_login:UserModel=Depends(require_notbanned), db_session:Session=Depends(get_db)):
    """提交评测"""
    problem_id = payload.problem_id
    db_problem = db.db_problem.get_problem(db=db_session, problem_id=problem_id)
    if db_problem is None:
        raise APIException(status_code=404, msg="题目不存在")

    language_name = payload.language_name
    db_language = db.db_language.get_language_by_name(db=db_session, name=language_name)
    if db_language is None:
        raise APIException(status_code=404, msg="语言不存在")

    db_submission = db.db_submission.add_submission(db=db_session, submission=payload, _problem_id=db_problem.id,language_id=db_language.id, user_id=db_login.id)
    db_login.submit_count += 1
    return {"msg": "success", "data": db_submission}

@router.get("/{submission_id}", response_model=ResponseModel[SubmissionResultResponse])
async def get_submission_result(submission_id:int, db_login:UserModel=Depends(require_login), db_session:Session=Depends(get_db)):
    """查询评测结果"""
    db_submission = db.db_submission.get_submission(db=db_session, submission_id=submission_id)

    if db_submission is None:
        raise APIException(status_code=404, msg="评测不存在")

    if db_login.role != "admin" and db_login.id != db_submission.user_id:
        raise APIException(status_code=403, msg="用户无权限")
    
    return {"msg": "success", "data": db_submission}

@router.get("/", response_model=ResponseModel[SubmissionListResponse])
async def get_submission_result_list(params:SubmissionQueryParams=Depends(), db_login:UserModel=Depends(require_login), db_session:Session=Depends(get_db)):
    """查询评测列表"""
    user_id = db_login.id
    is_admin = (db_login.role=="admin")

    if params.user_id is not None:
        if not is_admin and user_id != params.user_id:
            raise APIException(403, "权限不足")
    else:
        if not is_admin:
            raise APIException(403, "权限不足")
    
    if params.user_id is None and params.problem_id is None:
        raise APIException(400, "一级条件不可以全部为空")
    if params.page is not None and params.page_size is None:
        raise APIException(400, "参数错误")

    db_submission_list = db.db_submission.get_submission_list(
        db=db_session, user_id=user_id, problem_id=params.problem_id, status=params.status,
        page=params.page, page_size=params.page_size,
    )
    return {"msg": "success", "data": db_submission_list}

@router.put("/{submission_id}/rejudge", response_model=ResponseModel[SubmissionStatusResponse])
async def rejudge(submission_id:int, db_admin:UserModel=Depends(require_admin), db_session:Session=Depends(get_db)):
    """重新评测"""
    db_submission = db.db_submission.reset_submission(db=db_session, submission_id=submission_id)
    if db_submission is None:
        raise APIException(status_code=404, msg="评测不存在")
    
    return {"msg": "rejudge started", "data": db_submission}

@router.get("/{submission_id}/log", response_model=ResponseModel[Union[SubmissionLogResponse, SubmissionLogDetailResponse]])
async def get_submission_log(submission_id:int, db_login:UserModel=Depends(require_login), db_session:Session=Depends(get_db)):
    """查询评测日志"""
    db_submission = db.db_submission.get_submission(db=db_session, submission_id=submission_id)
    if db_submission is None:
        db.db_log.add_log(db=db_session, user_id=db_login.id, _problem_id=None, action="view_log", status=404)
        raise APIException(status_code=404, msg="评测不存在")
    
    db_problem = db.db_problem.get_problem_by_id(db=db_session, _problem_id=db_submission._problem_id)
    if db_problem is None:
        db.db_log.add_log(db=db_session, user_id=db_login.id, _problem_id=None, action="view_log", status=404)
        raise APIException(status_code=404, msg="题目不存在")
    if db_login.id != db_submission.user_id:
        if db_login.role != "admin" and not db_problem.log_visibility:
            db.db_log.add_log(db=db_session, user_id=db_login.id, _problem_id=db_submission._problem_id, action="view_log", status=403)
            raise APIException(status_code=403, msg="权限不足")
    
    data = None
    if db_problem.log_visibility:
        data = SubmissionLogDetailResponse.from_orm(db_submission)
    else:
        if db_login.role=="admin":
            data = SubmissionLogDetailResponse.from_orm(db_submission)
        else:
            data = SubmissionLogResponse.from_orm(db_submission)
    
    db.db_log.add_log(db=db_session, user_id=db_login.id, _problem_id=db_submission._problem_id, action="view_log", status=200)

    return {"msg": "success", "data": data}