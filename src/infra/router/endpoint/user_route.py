import secrets

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Response
from passlib.context import CryptContext
from starlette import status

from src.application.auth.auth import authenticate_user, create_access_token, get_current_user, get_current_user_optional
from src.application.dtos.user_create_dto import UserCreateDTO
from src.application.use_cases.user_usecase import UserUseCase
from src.domain.entities.user_schema import UserOut
from src.infra.database.models.user_model import UserModel
from src.infra.database.session import SessionLocal
from src.infra.dy.container import Container
from src.infra.router.schemas.user_requests import (
    AssignTimeRequest,
    ForgotPasswordRequest,
    LoginRequest,
    UserRegisterRequest,
)

router = APIRouter(prefix="/user")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/")
@inject
def create_user(
    user: UserCreateDTO,
    current_user: dict = Depends(get_current_user),
    usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    return usecase.create_user(user)


@router.get("/")
@inject
def list_users(usecase: UserUseCase = Depends(Provide[Container.user_usecase])):
    return usecase.list_users()


@router.get("/me")
def read_current_user(user: dict = Depends(get_current_user)):
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
def register_user(
    payload: UserRegisterRequest,
    current_user: dict | None = Depends(get_current_user_optional),
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    try:
        is_first_user = len(user_usecase.list_users()) == 0
        if is_first_user:
            role = "admin"
        elif current_user is None or current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Apenas admin pode cadastrar usuários.")
        else:
            role = payload.role

        hashed_password = pwd_context.hash(payload.password)
        user_data = UserCreateDTO(
            username=payload.username,
            full_name=payload.full_name,
            cpf=payload.cpf,
            hashed_password=hashed_password,
            role=role,
            subordinado_id=payload.subordinado_id,
            time_existente_id=payload.time_existente_id,
            novo_time=payload.novo_time,
            time_id=payload.time_id,
        )
        user_usecase.create_user(user_data)
        return {"message": "Usuário cadastrado com sucesso"}

    except HTTPException:
        raise
    finally:
        user_usecase.close()


@router.post("/forgot-password")
def reset_password(payload: ForgotPasswordRequest):
    db = SessionLocal()
    try:
        usuario = db.query(UserModel).filter_by(cpf=payload.cpf).first()

        if not usuario:
            raise HTTPException(status_code=404, detail="CPF não encontrado.")

        nova_senha = secrets.token_hex(4)
        usuario.hashed_password = pwd_context.hash(nova_senha)
        db.commit()

        return {"message": f"Sua nova senha é: {nova_senha}"}
    finally:
        db.close()


@router.post("/login")
def login(payload: LoginRequest, response: Response):
    user = authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})

    response.set_cookie(
        "access_token",
        f"Bearer {access_token}",
        httponly=True,
        secure=True,
        samesite="Lax",
    )
    return {"username": user["username"], "role": user["role"]}


@router.get("/gerentes", response_model=list[UserOut])
@inject
async def api_gerentes(
    current_user: dict = Depends(get_current_user),
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    if current_user["role"] not in ("coordenador", "admin"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    gerentes = user_usecase.list_by_role("gerente")
    result = [UserOut.model_validate(u, from_attributes=True) for u in gerentes]
    user_usecase.close()
    return result


@router.get("/colaboradores", response_model=list[UserOut])
@inject
async def search_colaboradores(
    q: str | None = None,
    current_user: dict = Depends(get_current_user),
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    if current_user["role"] not in ("gerente", "coordenador", "admin"):
        raise HTTPException(status_code=403, detail="Acesso negado")

    # Gerente só pode ver/associar colaboradores que ainda não têm time ou
    # que já são do próprio time — coordenador/admin veem todo mundo.
    time_ids = None
    if current_user["role"] == "gerente":
        time_ids = user_usecase.list_times_by_gerente(current_user["id"])

    colaboradores = user_usecase.search_colaboradores(q, time_ids)
    result = [UserOut.model_validate(u, from_attributes=True) for u in colaboradores]
    user_usecase.close()
    return result


@router.put("/{user_id}/time")
@inject
def assign_user_time(
    user_id: int,
    payload: AssignTimeRequest,
    current_user: dict = Depends(get_current_user),
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    if current_user["role"] != "gerente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        user = user_usecase.assign_time(user_id, payload.time_id)
        
        return {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "time_id": user.time_id,
        }
    finally:
        user_usecase.close()


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logout realizado com sucesso"}