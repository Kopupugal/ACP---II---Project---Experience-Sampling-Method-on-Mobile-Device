from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from backend.app.api.dependencies import DbSession
from backend.app.core.security import create_access_token, hash_password, verify_password
from backend.app.db.models import User
from backend.app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: DbSession) -> User:
    user = User(
        email=request.email.lower(),
        display_name=request.display_name,
        password_hash=hash_password(request.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email is already registered") from exc
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: DbSession) -> TokenResponse:
    user = db.query(User).filter(User.email == request.email.lower()).one_or_none()
    if user is None or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.email))
