from typing import List, Optional

from pydantic import BaseModel, constr


class UserCreateDTO(BaseModel):
    username: str
    full_name: str
    role: str
    cpf: constr(min_length=11, max_length=14)
    hashed_password: str
    campanhas: List[int] = []

    subordinado_id: Optional[int] = None
    time_existente_id: Optional[int] = None
    novo_time: Optional[str] = None
    time_id: Optional[int] = None


