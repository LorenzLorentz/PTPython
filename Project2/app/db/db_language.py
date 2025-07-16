from sqlalchemy.orm import Session
from app.db.models import LanguageModel
from app.schemas.language import LanguageAddPayload

def add_language(db:Session, language:LanguageAddPayload):
    """添加语言"""
    db_language = LanguageModel(**language.model_dump())
    db.add(db_language)
    db.commit()
    db.refresh(db_language)
    return db_language

def get_language_list(db:Session):
    """获取所有语言"""
    return db.query(LanguageModel).all()

def get_language_by_name(db:Session, name:str):
    """根据名字查找语言"""
    return db.query(LanguageModel).filter(LanguageModel.name == name).first()

def get_language_by_file_ext(db:Session, file_ext:str):
    """根据文件拓展名查找语言"""
    return db.query(LanguageModel).filter(LanguageModel.file_ext == file_ext).first()