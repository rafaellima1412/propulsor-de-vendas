from pydantic import BaseModel, constr


class UserCreateDTO(BaseModel):
    username: str
    full_name: str
    role: str
    cpf: constr(min_length=11, max_length=14)
    hashed_password: str
    campanhas: list[int] = []
