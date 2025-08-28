from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from db.db import get_db
from schemas.user_schema import UserCreate, UserOut, UserLogin, Token
from service import auth_service
from typing import Optional

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

def get_token_from_header(authorization: Optional[str] = Header(None)):
    """Extract token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        return token
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

@router.post("/logout/")
def logout_user(db: Session = Depends(get_db), token: str = Depends(get_token_from_header)):
    return auth_service.logout_user(db=db, token=token)
