from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.db import get_db
from schemas.user_schema import UserCreate, UserOut, UserLogin, Token
from service import auth_service

router = APIRouter()

@router.post("/register/", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = auth_service.create_user(db=db, user=user)
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail="Registration failed")

@router.post("/login/", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    return auth_service.login_user(db=db, email=user_credentials.email, password=user_credentials.password)
