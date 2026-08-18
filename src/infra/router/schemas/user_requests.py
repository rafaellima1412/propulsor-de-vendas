from pydantic import BaseModel, constr


class UserRegisterRequest(BaseModel):
    """Corpo JSON de POST /user/register. Senha em texto puro — o route é
    responsável por fazer o hash antes de repassar para o UserCreateDTO."""

    username: str
    full_name: str
    cpf: constr(min_length=11, max_length=14)
    password: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ForgotPasswordRequest(BaseModel):
    cpf: str
