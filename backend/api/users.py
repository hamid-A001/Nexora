from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.security import hash_password, verify_password
from backend.db.dependencies import get_db
from backend.models.user import User
from backend.schemas.user import UserCreate, UserLogin

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {
            "description": "Email already registered"
        }
    }
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    password_hash = hash_password(user.password)

    new_user = User(
        email=user.email,
        name=user.name,
        password_hash=password_hash
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    return {
        "message": "User registered successfully",
        "id": new_user.id,
        "email": new_user.email,
        "name": new_user.name
    }

@router.post("/login")
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(
        user.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        "id": existing_user.id,
        "email": existing_user.email,
        "name": existing_user.name
    }