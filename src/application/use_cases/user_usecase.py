from fastapi import HTTPException

from src.application.dtos.user_create_dto import UserCreateDTO
from src.application.repositories.iuser_repository import IUserRepository
from src.infra.database.models.user_model import UserModel


class UserUseCase:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def create_user(self, user: UserCreateDTO) -> UserModel:
        if self.user_repo.get_by_cpf(user.cpf):
            raise HTTPException(status_code=400, detail="CPF já está cadastrado.")
        if self.user_repo.get_by_username(user.username):
            raise HTTPException(status_code=400, detail="Username já está cadastrado.")

        new_user = UserModel(
            username=user.username,
            full_name=user.full_name,
            cpf=user.cpf,
            hashed_password=user.hashed_password,
            role=user.role,
        )

        # Coordenador e gerente não precisam de mais nada na criação — o
        # vínculo entre coordenador e campanha acontece depois, na tela
        # "Campanhas por coordenador". Colaborador entra em campanhas
        # específicas depois, via "Associar colaborador a campanha".
        return self.user_repo.create(new_user)

    def list_users(self) -> list[UserModel]:
        return self.user_repo.get_all()

    def get_user(self, user_id: int) -> UserModel | None:
        return self.user_repo.get_by_id(user_id)

    def list_by_role(self, role: str) -> list[UserModel]:
        return self.user_repo.get_by_role(role)

    def search_colaboradores(self, query: str | None = None) -> list[UserModel]:
        return self.user_repo.search_colaboradores(query)

    def list_colaboradores_by_coordenador(self, coordenador_id: int) -> list[UserModel]:
        return self.user_repo.get_colaboradores_by_coordenador(coordenador_id)

    def close(self):
        self.user_repo.db.close()
