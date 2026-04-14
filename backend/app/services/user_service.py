"""Minimal user persistence for MVP auth."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_or_create_user(db: Session, email: str) -> User:
    key = normalize_email(email)
    row = db.execute(select(User).where(User.email == key)).scalars().first()
    if row is not None:
        return row
    u = User(email=key, plan_id="free", is_active=True)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
