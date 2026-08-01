import secrets

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from passlib.context import CryptContext
from starlette import status

from src.application.auth.auth import authenticate_user, create_access_token, get_current_user
from src.application.dtos.user_create_dto import UserCreateDTO
from src.application.use_cases.user_usecase import UserUseCase
from src.domain.entities.user_schema import UserOut
from src.infra.database.models.user_model import UserModel
from src.infra.database.session import SessionLocal
from src.infra.dy.container import Container

router = APIRouter(prefix="/user")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def parse_optional_int(value: str | None) -> int | None:
    if value in (None, "", "null"):
        return None
    try:
        return int(value)
    except ValueError:
        return None


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
    username: str = Form(...),
    full_name: str = Form(...),
    cpf: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    subordinado_id: int | None = Form(None),
    novo_time: str | None = Form(None),
    time_existente_id: str | None = Form(None),
    time_id: int | None = Form(None),
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    try:
        hashed_password = pwd_context.hash(password)
        user_data = UserCreateDTO(
            username=username,
            full_name=full_name,
            cpf=cpf,
            hashed_password=hashed_password,
            role=role,
            subordinado_id=parse_optional_int(subordinado_id),
            time_existente_id=parse_optional_int(time_existente_id),
            novo_time=novo_time,
            time_id=parse_optional_int(time_id),
        )
        user_usecase.create_user(user_data)
        return {"message": "Usuário cadastrado com sucesso"}

    except HTTPException:
        raise
    finally:
        user_usecase.close()


@router.post("/forgot-password")
def reset_password(cpf: str = Form(...)):
    db = SessionLocal()
    try:
        usuario = db.query(UserModel).filter_by(cpf=cpf).first()

        if not usuario:
            raise HTTPException(status_code=404, detail="CPF não encontrado.")

        nova_senha = secrets.token_hex(4)
        usuario.hashed_password = pwd_context.hash(nova_senha)
        db.commit()

        # TODO: enviar a nova senha por e-mail/SMS em vez de retornar na resposta.
        return {"message": f"Sua nova senha é: {nova_senha}"}
    finally:
        db.close()


@router.post("/login")
def login(response: Response, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})

    # Cookie httponly continua sendo a forma mais segura de guardar o token.
    # Em dev com frontend em outra origem, use um proxy do Vite para /api
    # (mesma origem) OU sirva com SameSite="none"; Secure=True atrás de HTTPS.
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


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logout realizado com sucesso"}
