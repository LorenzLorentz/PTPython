from fastapi import APIRouter, Depends, Request, Path
from typing import List, Annotated
from sqlalchemy.orm import Session

from app import db
from app.db.database import get_db
from app.db.models import UserModel
from app.schemas.plagiarism_task import PlagiarismTaskLaunchPayload, PlagiarismTaskIDResponse, PlagiarismTaskReportResponse, PlagiarismTaskResultResponse
from app.schemas.response import ResponseModel
from app.api.utils.permission import require_admin
from app.api.utils.exception import APIException

router = APIRouter()

@router.post("/", response_model=ResponseModel[PlagiarismTaskIDResponse])
async def launch_plagiarism_task(payload:PlagiarismTaskLaunchPayload, db_admin:UserModel=Depends(require_admin), db_session:Session=Depends(get_db)):
    """
    发起查重检测
    参数: problem_id, submission_id, threshold (可选)
    权限: 管理员
    """
    problem_id = payload.problem_id
    db_problem = db.db_problem.get_problem(db=db_session, problem_id=problem_id)
    if db_problem is None:
        raise APIException(status_code=404, msg="题目不存在")

    submission_id = payload.submission_id
    db_submission = db.db_submission.get_submission(db=db_session, submission_id=submission_id)
    if db_submission is None:
        raise APIException(status_code=404, msg="提交不存在")

    db_task = db.db_task.add_task(db=db_session, submission_id=submission_id, _problem_id=db_problem.id, threshold=payload.threshold)
    return {"msg": "success", "data": db_task}

@router.get("/{task_id}", response_model=ResponseModel[PlagiarismTaskResultResponse])
async def  get_plagiarism_result(task_id:int, db_admin:UserModel=Depends(require_admin), db_session:Session=Depends(get_db)):
    """
    查询查重结果
    参数: 无
    权限: 管理员
    """
    db_task = db.db_task.get_task(db=db_session, task_id=task_id)
    if db_task is None:
        raise APIException(status_code=404, msg="查重任务不存在")
    
    return {"msg": "success", "data": db_task}

@router.get("/{task_id}/report", response_model=ResponseModel[PlagiarismTaskReportResponse])
async def get_pagiarism_report(task_id:int, db_admin:UserModel=Depends(require_admin), db_session:Session=Depends(get_db)):
    """
    下载查重报告
    参数: 无
    权限: 管理员
    """
    db_task = db.db_task.get_task(db=db_session, task_id=task_id)
    if db_task is None:
        raise APIException(status_code=404, msg="查重任务不存在")
    
    return {"msg": "success", "data": db_task}