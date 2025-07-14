from sqlalchemy.orm import Session

from app.db.models import UserModel, LanguageModel
from app.api.utils.security import get_password_hash

def seed_ini_data(db:Session):
    admin = db.query(UserModel).filter(UserModel.username == "admin").first()
    if admin:
        admin.username = "admin"
        admin.hashed_password = get_password_hash("admintestpassword")
        admin.role = "admin"
    else:
        admin = UserModel(
            username = "admin",
            hashed_password = get_password_hash("admintestpassword"),
            role = "admin",
        )
        db.add(admin)
    
    cpp = db.query(LanguageModel).filter(LanguageModel.name == "cpp").first()
    if not cpp:
        cpp = LanguageModel(
            name = "cpp",
            file_ext = ".cpp",
            compile_cmd = "g++ -std=c++14 main.cpp -o main",
            run_cmd = "./main",
            time_limit = 1.0,
            memory_limit = 256,
        )
        db.add(cpp)
    
    python = db.query(LanguageModel).filter(LanguageModel.name == "python").first()
    if not python:
        python = LanguageModel(
            name = "python",
            file_ext = ".py",
            run_cmd = "python main.py",
            time_limit = 2.0,
            memory_limit = 256,
        )
        db.add(python)
    
    db.commit()