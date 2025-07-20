from fastapi import APIRouter, Depends, Request, UploadFile, File
from typing import List
from sqlalchemy.orm import Session

from app import db
from app.db.database import get_db
from app.db.models import UserModel
from app.schemas.response import ResponseModel
from app.schemas.problem import (
    ProblemInfoResponse, ProblemBriefResponse, ProblemIDResponse, ProblemLogVisibilityResponse,
    ProblemAddPayload, ProblemSetLogVisibilityPayload, ProblemSetJudgeModePayload
)
from app.api.utils.permission import require_login, require_admin
from app.api.utils.exception import APIException

router = APIRouter()

@router.get("/", response_model=ResponseModel[List[ProblemBriefResponse]])
async def get_problems_list(db_login:UserModel=Depends(require_login), db_session:Session=Depends(get_db)):
    """
    查看题目列表
    参数: 无
    权限: 已登录用户
    """
    problem_list = db.db_problem.get_problem_list(db=db_session)
    
    return {"msg": "success", "data": problem_list}

@router.post("/", response_model=ResponseModel[ProblemIDResponse], status_code=200)
async def add_problem(payload:ProblemAddPayload, db_login:UserModel=Depends(require_login), db_session:Session=Depends(get_db)):
    """
    添加题目
    参数: 见ProblemAddPayload
    权限: 已登录用户
    """
    exist = db.db_problem.get_problem(db=db_session, problem_id=payload.problem_id)
    if exist:
        raise APIException(status_code=409, msg="id 已存在")

    if payload.judge_mode is not None and payload.judge_mode not in {"standard", "strict", "spj"}:
        raise APIException(status_code=400, msg="参数错误")

    db_problem = db.db_problem.add_problem(db=db_session, problem=payload)
    return {"msg": "add success", "data": db_problem}

@router.delete("/{problem_id}", response_model=ResponseModel[ProblemIDResponse])
async def delete_problem(problem_id:str, db_admin:UserModel=Depends(require_admin), db_session:Session=Depends(get_db)):
    """
    删除题目
    参数: 无
    权限: 管理员
    """
    db_problem = db.db_problem.delete_problem(db=db_session, problem_id=problem_id)
    
    if db_problem is None:
        raise APIException(status_code=404, msg="题目不存在")
    
    return {"msg": "delete success", "data": db_problem}

@router.get("/{problem_id}", response_model=ResponseModel[ProblemInfoResponse])
async def get_problem(problem_id:str, db_login:UserModel=Depends(require_login), db_session:Session=Depends(get_db)):
    """
    查看题目信息
    参数: problem_id
    权限: 已登录用户
    """
    problem = db.db_problem.get_problem(db=db_session, problem_id=problem_id)

    if problem is None:
        raise APIException(status_code=404, msg="题目不存在")

    return {"msg": "success", "data": problem}

@router.put("/{problem_id}/log_visibility", response_model=ResponseModel[ProblemLogVisibilityResponse])
async def set_log_visibility(problem_id:str, payload:ProblemSetLogVisibilityPayload, db_admin=Depends(require_admin), db_session=Depends(get_db)):
    """
    配置日志可见性
    参数: public_cases
    权限: 管理员
    """
    db_problem = db.db_problem.set_problem_log_visibility(db=db_session, problem_id=problem_id, log_visibility=payload.public_cases)
    if db_problem is None:
        raise APIException(status_code=404, msg="题目不存在")
    
    return {"msg": "log visibility updated", "data": db_problem}

@router.put("/{problem_id}/judge_mode")
async def set_judge_mode(problem_id:str, payload:ProblemSetJudgeModePayload, db_admin=Depends(require_admin), db_session=Depends(get_db)):
    """
    设置评测策略
    参数: problem_id, judge_mode
    权限: 管理员
    """
    db_problem = db.db_problem.set_problem_judge_mode(db=db_session, problem_id=problem_id, judge_mode=payload.judge_mode)
    if db_problem is None:
        raise APIException(status_code=404, msg="题目不存在")
    
    return {"msg": "judege mode updated", "data": db_problem}

@router.post("/{problem_id}/spj", response_model=ResponseModel[ProblemIDResponse])
async def upload_spj(problem_id:str, file:UploadFile=File(...), db_admin=Depends(require_admin), db_session=Depends(get_db)):
    """
    上传 SPJ 脚本
    参数: file
    权限: 管理员
    """
    code = await file.read()
    file_ext = None
    if file.filename.endswith(".cpp"):
        file_ext = ".cpp"
    elif file.filename.endswith(".py"):
        file_ext = ".py"

    db_language = db.db_language.get_language_by_file_ext(db=db_session, file_ext=file_ext)
    
    db_problem = db.db_problem.add_spj(db=db_session, problem_id=problem_id, language_id=db_language.id, code=code)
    if db_problem is None:
        raise APIException(status_code=404, msg="题目不存在")
    
    return {"msg": "add spj success", "data": db_problem}

@router.delete("/{problem_id}/spj", response_model=ResponseModel[ProblemIDResponse])
async def delete_spj(problem_id:str, db_admin=Depends(require_admin), db_session=Depends(get_db)):
    """
    删除 SPJ 脚本
    参数: 无
    权限: 管理员
    """
    db_problem = db.db_problem.delete_spj(db=db_session, problem_id=problem_id)
    if db_problem is None:
        raise APIException(status_code=404, msg="题目不存在")
    
    return {"msg": "delete spj success", "data": db_problem}