from sqlalchemy.orm import Session
from oj.db.models import LanguageModel
from oj.schemas.language import LanguageAddPayload
from oj.api.utils.security import get_password_hash

def add_language(db:Session, language:LanguageAddPayload,):
    db_language = LanguageModel(**language.model_dump())
    db.add(db_language)
    db.commit()
    db.refresh(db_language)
    return db_language

def get_language_list(db:Session):
    return db.query(LanguageModel).all()