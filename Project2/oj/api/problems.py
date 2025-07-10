from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List

from oj import db
from oj.db.database import get_db
from oj.schemas.response import ResponseModel
from oj.schemas.problem import Problem, ProblemAddPayload, ProblemID, ProblemBrief, ProblemSetLogVisibilityPayload, ProblemLogVisibility
from oj.api.utils.permission import check_admin, check_login

router = APIRouter()

@router.get("/", response_model=ResponseModel[List[ProblemBrief]])
async def get_problems_list(db_session=Depends(get_db)):
    """查看题目列表"""
    problem_list = db.db_problem.get_problem_list(db=db_session)
    
    return {"msg": "success", "data": problem_list}

@router.post("/", response_model=ResponseModel[ProblemID], status_code=200)
async def add_problem(payload:ProblemAddPayload, db_session=Depends(get_db)):
    """添加题目"""
    exist = db.db_problem.get_problem(db=db_session, problem_id=payload.id)
    if exist:
        raise HTTPException(status_code=409, detail="id 已存在")

    db_problem = db.db_problem.add_problem(db=db_session, problem=payload)
    return {"msg": "add success", "data": db_problem}

@router.delete("/{problem_id}", response_model=ResponseModel[List[ProblemID]])
async def delete_problem(request:Request, problem_id:int, db_session=Depends(get_db)) -> dict:
    """删除题目"""
    if not check_admin(request=request, db_session=db_session):
        raise HTTPException(status_code=403, detail="权限不足")

    db_problem = db.db_problem.delete_problem(db=db_session, problem_id=problem_id)
    
    if db_problem is None:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    return {"msg": "delete success", "data": db_problem}

@router.get("/{problem_id}", response_model=ResponseModel[Problem])
async def get_problem(problem_id:int, db_session=Depends(get_db)) -> dict:
    """查看题目信息"""
    problem = db.db_problem.get_problem(db=db_session, problem_id=problem_id)

    if problem is None:
        raise HTTPException(status_code="404", detail="题目不存在")

    return {"msg": "success", "data": problem}

@router.put("/{problem_id}/log_visibility", response_model=ResponseModel[ProblemLogVisibility])
async def set_log_visibility(request:Request, problem_id:str, payload:ProblemSetLogVisibilityPayload, db_session=Depends(get_db)):
    """配置日志/测例可见性"""
    if not check_login(request=request, db_session=db_session):
        raise HTTPException(status_code=401, detail="用户未登录")

    if not check_admin(request=request, db_session=db_session):
        raise HTTPException(status_code=403, detail="用户无权限")
    
    db_problem = db.db_problem.set_problem_log_visibility(db=db_session, problem_id=problem_id, log_visibility=payload.public_cases)
    if db_problem is None:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    return db_problem