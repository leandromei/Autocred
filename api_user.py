from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from crud_user import *
from schemas_user import User as UserSchema, UserCreate, UserUpdate
from database import get_db
# Import authentication dependency later
# from core_security import get_current_active_superuser # Example dependency

# Assuming this router will be mounted under /api/admin
router = APIRouter(prefix="/users")

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    # current_user: models_user.User = Depends(get_current_active_superuser) # Add auth later
):
    """Create a new user."""
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    return create_user(db=db, user=user_in)

@router.get("/", response_model=List[UserSchema])
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    # current_user: models_user.User = Depends(get_current_active_superuser) # Add auth later
):
    """Retrieve a list of users."""
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    # current_user: models_user.User = Depends(get_current_active_superuser) # Add auth later
):
    """Retrieve a specific user by ID."""
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    # current_user: models_user.User = Depends(get_current_active_superuser) # Add auth later
):
    """Update a user."""
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Check for email conflict if email is being updated
    if user_in.email and user_in.email != db_user.email:
        existing_user = get_user_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered by another user."
            )
    return update_user(db=db, db_user=db_user, user_in=user_in)

@router.delete("/{user_id}", response_model=UserSchema)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    # current_user: models_user.User = Depends(get_current_active_superuser) # Add auth later
):
    """Delete a user."""
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Add logic here to prevent self-deletion or deletion of critical users if needed
    return delete_user(db=db, db_user=db_user)

