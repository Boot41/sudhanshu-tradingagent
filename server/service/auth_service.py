from sqlalchemy.orm import Session
from model.model import User
from schemas.user_schema import UserCreate
from core.security import get_password_hash
from fastapi import HTTPException

def create_user(db: Session, user: UserCreate):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, username=user.username, phone=user.phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
