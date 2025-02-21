from app import models, database
from sqlalchemy.orm import Session

def create_user(db: Session, name: str, email: str):
    db_user = models.User(name=name, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # Tải lại user từ DB để có ID được tạo tự động
    return db_user

def get_users(db: Session):
    return db.query(models.User).all()

def main():
    db = database.SessionLocal() # Tạo session database

    # Tạo người dùng mới
    new_user = create_user(db, name="John Doenew", email="john1.doe@example.com")
    print(f"Created user: {new_user}")

    # Lấy danh sách người dùng
    users = get_users(db)
    print("\nList of users:")
    for user in users:
        print(user)

    db.close() # Đóng session khi dùng xong

if __name__ == "__main__":
    main()