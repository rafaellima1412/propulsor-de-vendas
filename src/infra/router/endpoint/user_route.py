import secrets

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Response
from passlib.context import CryptContext
from starlette import status

from src.application.auth.auth import authenticate_user, create_access_token, get_current_user
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
    usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    return usecase.create_user(user)


@router.get("/")
@inject
def list_users(usecase: UserUseCase = Depends(Provide[Container.user_usecase])):
    return usecase.list_users()


@router.get("/me")
def read_current_user(user: dict = Depends(get_current_user)):
    """Retorna o usuário autenticado. O frontend chama isso ao carregar para saber se há sessão válida."""
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
@inject
def register_user(
    payload: UserRegisterRequest,
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    try:
        hashed_password = pwd_context.hash(payload.password)
        user_data = UserCreateDTO(
            username=payload.username,
            full_name=payload.full_name,
            cpf=payload.cpf,
            hashed_password=hashed_password,
            role=payload.role,
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
async def api_gerentes(user_usecase: UserUseCase = Depends(Provide[Container.user_usecase])):
    gerentes = user_usecase.list_by_role("gerente")
    result = [UserOut.model_validate(u, from_attributes=True) for u in gerentes]
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
    """Associa um usuário existente a um time (resolve 'usuário não está
    associado a nenhum time' quando ele foi cadastrado sem time_id)."""
    if current_user["role"] not in ["gerente", "coo"]:
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