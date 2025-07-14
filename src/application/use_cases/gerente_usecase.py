from typing import List
from src.application.repositories.igerente_repository import IGerenteRepository
from src.domain.entities.user_schema import UserBase, UserCreate


class GerenteUseCases:
    def __init__(self, repo: IGerenteRepository):
        self.repo = repo

    def list_gerentes(self) -> List[UserBase]:
        return self.repo.list_all()

    def create_gerente(self, data: UserCreate) -> UserBase:
        novo_gerente = UserBase(**data.dict())
        return self.repo.create(novo_gerente)

    def update_gerente(self, id: int, data: UserCreate) -> UserBase:
        gerente = self.repo.get_by_id(id)
        if not gerente:
            raise ValueError("Gerente não encontrado")
        gerente.name = data.nome
        gerente.coo_id = data.coo_id
        return self.repo.update(gerente)

    def delete_gerente(self, id: int) -> None:
        self.repo.delete(id)