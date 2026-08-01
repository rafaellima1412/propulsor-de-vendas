import secrets
from typing import Optional, List

from dependency_injector.wiring import inject, Provide
from fastapi import Request, Form, Depends, APIRouter, HTTPException
from passlib.context import CryptContext
from starlette import status
from starlette.responses import RedirectResponse, HTMLResponse, JSONResponse
from starlette.templating import Jinja2Templates

from src.application.auth.auth import authenticate_user, create_access_token, get_current_user
from src.application.dtos.user_create_dto import UserCreateDTO
from src.application.use_cases.gerente_usecase import GerenteUseCases
from src.application.use_cases.user_usecase import UserUseCase
from src.domain.entities.user_schema import UserOut
from src.infra.database.models.user_model import UserModel

from src.infra.database.session import SessionLocal
from src.infra.dy.container import Container

router = APIRouter(prefix="/user")

templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def parse_optional_int(value: Optional[str]) -> Optional[int]:
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




@router.post("/register")
@inject
def register_user(
    request: Request,
    username: str = Form(...),
    full_name: str = Form(...),
    cpf: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    subordinado_id: Optional[int] = Form(None),
    novo_time: Optional[str] = Form(None),
    time_existente_id: Optional[str] = Form(None),
    time_id: Optional[int] = Form(None),


    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase])
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
        # print("DEBUG create_user:", user_data)
        user_usecase.create_user(user_data)
        return RedirectResponse(url="/user/register", status_code=status.HTTP_302_FOUND)

    except HTTPException as e:
        print("Erro:", getattr(e, 'detail', str(e)))
        response = templates.TemplateResponse(
            request,
            "register.html",
            {
                "error": e.detail,
                "user": None,
                "gerentes": user_usecase.list_by_role("gerente"),
                "time": user_usecase.list_all_times(),
            },
        )
        user_usecase.close()
        return response

@router.get("/forgot-password")
def show_forgot_password(request: Request):
    return templates.TemplateResponse(
        request,
        "forgot_password.html", 
        {"user": None})

@router.post("/forgot-password")
def reset_password(request: Request, cpf: str = Form(...)):
    db = SessionLocal()
    usuario = db.query(UserModel).filter_by(cpf=cpf).first()

    if not usuario:
        return templates.TemplateResponse(
            request, 
            "forgot_password.html", 
            {"error": "CPF não encontrado.", "user": None})

    nova_senha = secrets.token_hex(4)
    print(nova_senha)
    usuario.hashed_password = pwd_context.hash(nova_senha)
    db.commit()
    db.close()

    return templates.TemplateResponse(
        request,
        "forgot_password.html", {
        "message": f"Sua nova senha é: {nova_senha}"
    })


@router.post("/cadastro", response_class=HTMLResponse)
def login_web(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)):
    user = authenticate_user(username, password)
    if user:
        access_token = create_access_token(data={
            "sub": user["username"],
            "role": user["role"]
        })
        response = RedirectResponse(url="/pagina/inicial", status_code=status.HTTP_302_FOUND)
        response.set_cookie("access_token", f"Bearer {access_token}", httponly=True,secure=True, samesite="Lax")
        return response
    return templates.TemplateResponse(
    request,
    "login.html",
    {
        "error": "Credenciais inválidas",
        "user": None,
    },
)


@router.get("/register")
@inject
def show_register_form(
    request: Request,
    user: dict = Depends(get_current_user),
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    response = templates.TemplateResponse(
        request,
        "register.html", {
        "user": user,
        "gerentes": user_usecase.list_by_role("gerente"),
        "time": user_usecase.list_all_times(),
    })
    user_usecase.close()
    return response

@router.get("/gerentes", response_model=List[UserOut])
@inject
async def api_gerentes(
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase])
):
    gerentes = user_usecase.list_by_role("gerente")
    result = [UserOut.model_validate(u, from_attributes=True) for u in gerentes]
    user_usecase.close()
    return result


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response