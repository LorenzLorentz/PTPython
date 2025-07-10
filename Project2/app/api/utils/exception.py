from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class APIException(Exception):
    def __init__(self, status_code:int, msg:str):
        self.status_code = status_code
        self.msg = msg