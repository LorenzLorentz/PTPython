from fastapi import APIRouter

router = APIRouter()

@router.get(
    "/",
)
async def get_problems_list() -> dict:
    """查看题目列表。"""
    all_problems = [
        {"id": "sum_2", "title": "两数之和"},
        {"id": "max_num", "title": "最大数"}
    ]
    
    return {
        "code": 200,
        "msg": "success",
        "data": all_problems
    }