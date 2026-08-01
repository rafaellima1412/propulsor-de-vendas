from src.application.repositories.igerente_repository import IGerenteRepository
from src.domain.entities.user_schema import UserCreate, UserOut
from src.infra.database.models import UserModel


class GerenteUseCases:
    def __init__(self, repo: IGerenteRepository):
        self.repo = repo

    def list_gerentes(self) -> list[UserOut]:
        users = self.repo.list_all()
        return [UserOut.from_orm(u) for u in users]

    def create_gerente(self, data: UserCreate) -> UserOut:
        novo_gerente = UserModel(**data.dict())
        return self.repo.create(novo_gerente)

    def update_gerente(self, id: int, data: UserCreate) -> UserOut:
        gerente = self.repo.get_by_id(id)
        if not gerente:
            raise ValueError("Gerente não encontrado")
        gerente.name = data.name
        gerente.coo_id = data.coo_id
        return self.repo.update(gerente)

    def delete_gerente(self, id: int) -> None:
        self.repo.delete(id)
