from app.database.db import Base, engine
from app.database import models

# Tạo các bảng trong database (chỉ cần chạy 1 lần khi khởi tạo)
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created!")
