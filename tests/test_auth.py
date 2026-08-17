from datetime import timedelta

import pytest
from jose import jwt

from src.application.auth.auth import create_access_token, pwd_context, verify_password
from src.infra.settings.settings import settings

pytestmark = pytest.mark.unit


def test_password_hash_roundtrip():
    hashed = pwd_context.hash("super-secret-123")

    assert hashed != "super-secret-123"
    assert verify_password("super-secret-123", hashed) is True


def test_wrong_password_fails_verification():
    hashed = pwd_context.hash("super-secret-123")

    assert verify_password("wrong-password", hashed) is False


def test_create_access_token_contains_expected_claims():
    token = create_access_token(data={"sub": "rafael", "role": "coordenador"})

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert payload["sub"] == "rafael"
    assert payload["role"] == "coordenador"
    assert "exp" in payload


def test_create_access_token_respects_custom_expiration():
    token = create_access_token(data={"sub": "rafael"}, expires_delta=timedelta(minutes=1))

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "rafael"
