from fastapi import APIRouter, HTTPException, status

from app.schemas import LoginRequest, TokenResponse
from app.services.auth import authenticate_user, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest) -> TokenResponse:
    if not authenticate_user(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario ou senha invalidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token(credentials.username))

