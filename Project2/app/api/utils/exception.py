from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class APIException(Exception):
    """自定义错误类型, 错误响应格式为: {"code": 404, "msg": "problem not found", "data": null}"""
    def __init__(self, status_code:int, msg:str):
        self.status_code = status_code
        self.msg = msg