from sqlalchemy.orm import Session

from app.db.database import Base, engine, SessionLocal
from app.db.models import UserModel, LanguageModel
from app.api.utils.security import get_password_hash

def seed_ini_data(db:Session):
    cpp = db.query(LanguageModel).filter(LanguageModel.name == "cpp").first()
    python = db.query(LanguageModel).filter(LanguageModel.name == "python").first()
    admin = db.query(UserModel).filter(UserModel.username == "admin").first()
    
    if not admin:
        admin = UserModel(
            username = "admin",
            hashed_password = get_password_hash("admin"),
            role = "admin",
        )
        db.add(admin)
    else:
        admin.username = "admin"
        admin.hashed_password = get_password_hash("admin")
        admin.role = "admin"

    if not cpp:
        cpp = LanguageModel(
            name = "cpp",
            file_ext = ".cpp",
            compile_cmd = "g++ -std=c++14 main.cpp -o main.o",
            run_cmd = "./main.o",
            time_limit = 1.0,
            memory_limit = 256,
        )
        db.add(cpp)

    if not python:
        python = LanguageModel(
            name = "python",
            file_ext = ".py",
            run_cmd = "python main.py",
            time_limit = 2.0,
            memory_limit = 256,
        )
        db.add(python)