from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user
from app.core.tokens import create_access_token
from app.db.session import SessionLocal
from app.schemas.api_contracts import SessionCreateRequest, SessionResponse, UserSummary
from app.services.user_service import get_or_create_user

router = APIRouter(tags=["auth"])


@router.post("/auth/session", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(body: SessionCreateRequest) -> SessionResponse:
    db = SessionLocal()
    try:
        user = get_or_create_user(db, str(body.email))
        email = user.email or ""
        token = create_access_token(user_id=user.id, email=email)
        return SessionResponse(
            access_token=token,
            user=UserSummary(id=user.id, email=email),
        )
    finally:
        db.close()


@router.get("/auth/me", response_model=UserSummary)
def read_me(user: Annotated[UserSummary, Depends(get_current_user)]) -> UserSummary:
    return user
