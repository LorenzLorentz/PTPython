from fastapi import APIRouter, Depends, Request, UploadFile, File
from typing import List

from app import db
from app.db.database import get_db
from app.schemas.response import ResponseModel
from app.schemas.problem import (
    ProblemInfoResponse, ProblemBriefResponse, ProblemIDResponse, ProblemLogVisibilityResponse,
    ProblemAddPayload, ProblemSetLogVisibilityPayload
)
from app.api.utils.permission import check_admin, check_login
from app.api.utils.exception import APIException

router = APIRouter()

@router.get("/", response_model=ResponseModel[List[ProblemBriefResponse]])
async def get_problems_list(db_session=Depends(get_db)):
    """查看题目列表"""
    problem_list = db.db_problem.get_problem_list(db=db_session)
    
    return {"msg": "success", "data": problem_list}

@router.post("/", response_model=ResponseModel[ProblemIDResponse], status_code=200)
async def add_problem(payload:ProblemAddPayload, db_session=Depends(get_db)):
    """添加题目"""
    exist = db.db_problem.get_problem(db=db_session, problem_id=payload.problem_id)
    if exist:
        raise APIException(status_code=409, msg="id 已存在")

    db_problem = db.db_problem.add_problem(db=db_session, problem=payload)
    return {"msg": "add success", "data": db_problem}

@router.delete("/{problem_id}", response_model=ResponseModel[ProblemIDResponse])
async def delete_problem(request:Request, problem_id:str, db_session=Depends(get_db)) -> dict:
    """删除题目"""
    if not check_admin(request=request, db_session=db_session):
        raise APIException(status_code=403, msg="权限不足")

    db_problem = db.db_problem.delete_problem(db=db_session, problem_id=problem_id)
    
    if db_problem is None:
        raise APIException(status_code=404, msg="题目不存在")
    
    return {"msg": "delete success", "data": db_problem}

@router.get("/{problem_id}", response_model=ResponseModel[ProblemInfoResponse])
async def get_problem(problem_id:str, db_session=Depends(get_db)) -> dict:
    """查看题目信息"""
    problem = db.db_problem.get_problem(db=db_session, problem_id=problem_id)

    if problem is None:
        raise APIException(status_code=404, msg="题目不存在")

    return {"msg": "success", "data": problem}

@router.put("/{problem_id}/log_visibility", response_model=ResponseModel[ProblemLogVisibilityResponse])
async def set_log_visibility(request:Request, problem_id:str, payload:ProblemSetLogVisibilityPayload, db_session=Depends(get_db)):
    """配置日志/测例可见性"""
    if not check_login(request=request, db_session=db_session):
        raise APIException(status_code=401, msg="用户未登录")

    if not check_admin(request=request, db_session=db_session):
        raise APIException(status_code=403, msg="用户无权限")
    
    db_problem = db.db_problem.set_problem_log_visibility(db=db_session, problem_id=problem_id, log_visibility=payload.public_cases)
    if db_problem is None:
        raise APIException(status_code=404, msg="题目不存在")
    
    return {"msg": "log visibility updated", "data": db_problem}

@router.post("/{problem_id}/spj", response_model=ResponseModel[ProblemIDResponse])
async def upload_spj(request:Request, problem_id:str, file:UploadFile=File(...), db_session=Depends(get_db)):
    """上传 SPJ 脚本"""
    if not check_login(request=request, db_session=db_session):
        raise APIException(status_code=401, msg="用户未登录")

    if not check_admin(request=request, db_session=db_session):
        raise APIException(status_code=403, msg="用户无权限")

    spj = {
        "file_ext": file.filename,
        "content": await file.read(),
    }

    db_problem = db.db_problem.add_spj(db=db_session, problem_id=problem_id, spj=spj)
    if db_problem is None:
        raise APIException(status_code=404, msg="题目不存在")
    
    return {"msg": "add spj success", "data": db_problem}

@router.delete("/{problem_id}/spj", response_model=ResponseModel[ProblemIDResponse])
async def delete_spj(request:Request, problem_id:str, db_session=Depends(get_db)):
    """删除 SPJ 脚本"""
    if not check_login(request=request, db_session=db_session):
        raise APIException(status_code=401, msg="用户未登录")

    if not check_admin(request=request, db_session=db_session):
        raise APIException(status_code=403, msg="用户无权限")
    
    db_problem = db.db_problem.delete_spj(db=db_session, problem_id=problem_id)
    if db_problem is None:
        raise APIException(status_code=404, msg="题目不存在")
    
    return {"msg": "delete spj success", "data": db_problem}