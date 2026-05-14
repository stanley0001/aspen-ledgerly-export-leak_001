from __future__ import annotations

import secrets
from typing import Dict

from fastapi import Header, HTTPException, status

from ledgerly.models import User, store


_TOKENS: Dict[str, str] = {}


def login(username: str, password: str) -> User | None:
    user = store.get_user(username)
    if not user or user.password != password:
        return None
    return user


def issue_token(user: User) -> str:
    token = secrets.token_hex(16)
    _TOKENS[token] = user.username
    return token


def resolve(token: str) -> User | None:
    username = _TOKENS.get(token)
    if not username:
        return None
    return store.get_user(username)


def current_user(authorization: str | None = Header(default=None)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = authorization.split(" ", 1)[1]
    user = resolve(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return user


def require_admin(user: User) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


def _clear_tokens() -> None:
    _TOKENS.clear()
