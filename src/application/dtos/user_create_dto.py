from pydantic import BaseModel, constr


class UserCreateDTO(BaseModel):
    username: str
    full_name: str
    role: str
    cpf: constr(min_length=11, max_length=14)
    matricula: str | None = None
    hashed_password: str
    campanhas: list[int] = []

    subordinado_id: int | None = None
    time_existente_id: int | None = None
    novo_time: str | None = None
    time_id: int | None = None