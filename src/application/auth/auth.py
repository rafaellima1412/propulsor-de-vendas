from datetime import datetime, timedelta, UTC

from dependency_injector.wiring import inject, Provide
from fastapi import Request, HTTPException, Depends
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.application.repositories.iuser_repository import IUserRepository
from src.infra.dy.container import Container

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from src.infra.settings.settings import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

@inject
def authenticate_user(
    username: str,
    password: str,
    user_repository: IUserRepository = Depends(Provide[Container.user_repository])
) -> dict | None:
    user = user_repository.get_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return {"username": user.username, "role": user.role}

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@inject
def get_current_user(
    request: Request,
    user_repository: IUserRepository = Depends(Provide[Container.user_repository])
) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token não encontrado")

    try:
        payload = jwt.decode(token.split(" ")[1], settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        # role = payload.get("role")
        if username is None:
            raise JWTError()

        user = user_repository.get_by_username(username)
        if not user:
            raise HTTPException(status_code=401, detail="Usuário não existe")

        return {"id": user.id,"username": user.username, "role": user.role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
