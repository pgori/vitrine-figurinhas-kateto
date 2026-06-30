import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

AUTH_USERNAME = os.getenv("BACKEND_AUTH_USERNAME", "admin")
AUTH_PASSWORD = os.getenv("BACKEND_AUTH_PASSWORD", "admin")
TOKEN_SECRET = os.getenv("BACKEND_TOKEN_SECRET", "dev-secret-change-me")
TOKEN_TTL_SECONDS = int(os.getenv("BACKEND_TOKEN_TTL_SECONDS", "28800"))

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedUser:
    username: str


class AuthTokenError(Exception):
    pass


def authenticate_user(username: str, password: str) -> bool:
    username_matches = secrets.compare_digest(username, AUTH_USERNAME)
    password_matches = secrets.compare_digest(password, AUTH_PASSWORD)
    return username_matches and password_matches


def create_access_token(username: str) -> str:
    expires_at = int(time.time()) + TOKEN_TTL_SECONDS
    payload = {"sub": username, "exp": expires_at}
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = _sign(encoded_payload)

    return f"{encoded_payload}.{signature}"


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais ausentes.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        username = verify_access_token(credentials.credentials)
    except AuthTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token invalido ou expirado.",
        ) from None

    return AuthenticatedUser(username=username)


def verify_access_token(token: str) -> str:
    try:
        encoded_payload, signature = token.split(".", maxsplit=1)
    except ValueError:
        raise AuthTokenError("Formato invalido.") from None

    expected_signature = _sign(encoded_payload)
    if not secrets.compare_digest(signature, expected_signature):
        raise AuthTokenError("Assinatura invalida.")

    payload = _decode_payload(encoded_payload)
    subject = payload.get("sub")
    expires_at = payload.get("exp")

    if not isinstance(subject, str) or not subject:
        raise AuthTokenError("Assunto invalido.")

    if not isinstance(expires_at, int) or expires_at < int(time.time()):
        raise AuthTokenError("Token expirado.")

    return subject


def _decode_payload(encoded_payload: str) -> dict[str, Any]:
    try:
        raw_payload = _base64url_decode(encoded_payload)
        payload = json.loads(raw_payload)
    except (ValueError, json.JSONDecodeError):
        raise AuthTokenError("Payload invalido.") from None

    if not isinstance(payload, dict):
        raise AuthTokenError("Payload invalido.")

    return payload


def _sign(encoded_payload: str) -> str:
    signature = hmac.new(
        TOKEN_SECRET.encode(),
        encoded_payload.encode(),
        hashlib.sha256,
    ).digest()
    return _base64url_encode(signature)


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _base64url_decode(value: str) -> bytes:
    padded_value = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded_value.encode())

