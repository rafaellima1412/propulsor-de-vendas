from pydantic import BaseModel, constr


class UserRegisterRequest(BaseModel):
    """Corpo JSON de POST /user/register. Senha em texto puro — o route é
    responsável por fazer o hash antes de repassar para o UserCreateDTO."""

    username: str
    full_name: str
    cpf: constr(min_length=11, max_length=14)
    matricula: str | None = None
    password: str
    role: str
    subordinado_id: int | None = None
    novo_time: str | None = None
    time_existente_id: int | None = None
    time_id: int | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class ForgotPasswordRequest(BaseModel):
    cpf: str


class AssignTimeRequest(BaseModel):
    time_id: int