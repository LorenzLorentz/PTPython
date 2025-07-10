from fastapi import APIRouter, Depends, HTTPException, Request, Path
from typing import List, Annotated

from oj import db
from oj.db.database import get_db
from oj.schemas.submission import SubmissionAddPayload, SubmissionResult, SubmissionStatus, SubmissionQueryPayload, SubmissionList
from oj.schemas.response import ResponseModel
from oj.api.utils.permission import check_admin, check_login, check_banned

router = APIRouter()

@router.post("/", response_model=ResponseModel[SubmissionStatus])
async def submit(request:Request, payload:SubmissionAddPayload, db_session=Depends(get_db)):
    """提交评测"""
    if check_login(request=request, db_session=db_session):
        raise HTTPException(status_code=401, detail="未登录")
    
    if check_banned(request=request, db_session=db_session):
        raise HTTPException(status_code=403, detail="用户被禁用")

    problem_id = payload.problem_id
    db_problem = db.db_problem.get_problem(db=db_session, problem_id=problem_id)
    if db_problem is None:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # 提交频率超限

    db_submission = db.db_submission.add_submission(db=db_session, submission=payload, user_id=request.session.get("user_id"))
    return {"msg": "success", "data": db_submission}

@router.get("/{submission_id}", response_model=ResponseModel[SubmissionResult])
async def get_submission_result(request:Request, submission_id:int, db_session=Depends(get_db)):
    """查询评测结果"""
    db_submission = db.db_submission.get_submission(db=db_session, submission_id=submission_id)

    if db_submission is None:
        raise HTTPException(404, "评测不存在")

    user_id = request.session.get("user_id")
    if user_id is not db_submission.user_id:
        db_user = db.db_user.get_user(db=db_session, user_id=user_id)
        if db_user is None:
            raise HTTPException(403, "权限不足")
        if db_user.user_id is not "admin":
            raise HTTPException(403, "权限不足")
    
    return {"msg": "success", "data": db_submission}

@router.get("/", response_model=ResponseModel[SubmissionList])
async def get_submission_result_list(request:Request, payload:SubmissionQueryPayload, db_session=Depends(get_db)):
    """查询评测列表"""
    if payload.user_id is None:
        if not check_admin(request=request, db_session=db_session):
            raise HTTPException(403, "权限不足")
    else:
        user_id = request.session.get("user_id")
        if user_id is not payload.user_id:
            db_user = db.db_user.get_user(db=db_session, user_id=user_id)
            if db_user is None:
                raise HTTPException(403, "权限不足")
            if db_user.user_id is not "admin":
                raise HTTPException(403, "权限不足")
            
    db_submission_list = db.db_submission.get_submission_list()
    return {"msg": "success", "data": db_submission_list}

@router.put("/{submission_id}/rejudge")
async def rejudge():
    """重新评测"""
    pass

@router.get("/{submission_id}/log", response_model=ResponseModel[SubmissionStatus])
async def get_submission_log(request:Request, submission_id:int, db_session=Depends(get_db)):
    """查询评测日志"""
    if not check_admin(request=request, db_session=db_session):
        raise HTTPException(status_code=403, detail="权限不足")

    db_submission = db.db_submission.reset_submission(db=db_session)
    if db_submission is None:
        raise HTTPException(status_code=404, detail="评测不存在")
    
    return db_submission