from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.api import api_router
from starlette.middleware.sessions import SessionMiddleware
from app.api.utils.exception import APIException
from app.db.database import SessionLocal, Base, engine
from app.api.utils.data import seed_ini_data, seed_other_data

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_ini_data(db)
    # seed_other_data(db)

app = FastAPI(title="OJ System")

# 注册中间件和路由
app.add_middleware(SessionMiddleware, secret_key="PYTHON")
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to OJ"}

"""修改Pydantic参数解析报错码"""
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request:Request, exc:RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 400,
            "msg": "参数错误",
            "detail": exc.errors() 
        },
    )

"""注册自定义异常"""
@app.exception_handler(APIException)
async def api_exception_handler(request:Request, exc:APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "msg": exc.msg,
            "data": None
        }
    )