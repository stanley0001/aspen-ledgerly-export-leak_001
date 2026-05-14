from fastapi import APIRouter, HTTPException, status

from ledgerly import auth as auth_service
from ledgerly.schemas import LoginRequest


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest):
    user = auth_service.login(payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = auth_service.issue_token(user)
    return {"token": token, "username": user.username, "role": user.role}
