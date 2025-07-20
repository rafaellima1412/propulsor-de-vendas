from typing import List, Optional
from fastapi import HTTPException
from src.application.dtos.user_create_dto import UserCreateDTO
from src.application.repositories.ITimeRepository import ITimeRepository
from src.application.repositories.iuser_repository import IUserRepository
from src.domain.entities.time_schema import TimeCreate, TimeUpdate
from src.infra.database.models.time_model import TimeModel
from src.infra.database.models.user_model import UserModel
from sqlalchemy.orm import Session





class UserUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        time_repo: ITimeRepository,
    ):
        self.user_repo = user_repo
        self.time_repo = time_repo

    def create_user(self, user: UserCreateDTO) -> UserModel:
        # print("📥 Dados recebidos:", user.model_dump())
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

        new_user = self.user_repo.create(new_user)

        if user.role == "gerente":
            if user.novo_time and user.novo_time.strip():
                time = self.time_repo.get_by_name(user.novo_time)
                if not time:
                    time_data = TimeCreate(
                        name=user.novo_time,
                        gerente_id=new_user.id,
                        coo_id=new_user.id
                    )
                    time = self.time_repo.create(time_data)
                new_user.time_id = time.id
                self.user_repo.update(new_user)
            elif user.time_existente_id:
                new_user.time_id = user.time_existente_id
                self.user_repo.update(new_user)
            else:
                raise HTTPException(status_code=400, detail="Time obrigatório para gerente.")

        elif user.role == "colaborador":
            print("📦 Recebido time_id para colaborador:", user.time_id)
            if user.time_id:
                new_user.time_id = user.time_id
                self.user_repo.update(new_user)

        elif user.role == "coo":
            if user.subordinado_id:
                # Buscar o time do gerente subordinado
                subordinado = self.user_repo.get_by_id(user.subordinado_id)
                if not subordinado or subordinado.role != "gerente":
                    raise HTTPException(status_code=404, detail="Gerente subordinado não encontrado.")

                # Atualiza o time(s) que o gerente lidera para ter esse COO
                times = self.time_repo.get_by_gerente(subordinado.id)
                for time in times:
                    time.coo_id = new_user.id
                    time_update_data = TimeUpdate.from_orm(time)
                    self.time_repo.update(time.id, time_update_data)
            else:
                raise HTTPException(status_code=400, detail="COO deve selecionar um gerente subordinado.")

        return new_user

    def list_users(self) -> List[UserModel]:
        return self.user_repo.get_all()

    def get_user(self, user_id: int) -> Optional[UserModel]:
        return self.user_repo.get_by_id(user_id)

    def list_by_role(self, role: str) -> List[UserModel]:
        return self.user_repo.get_by_role(role)

    def list_gerentes_by_coo(self, coo_id: int) -> List[UserModel]:
        return self.user_repo.get_gerentes_by_coo(coo_id)
    #
    # def list_times_ids_by_gerente(self, gerente_id: int) -> List[int]:
    #     return self.user_repo.get_times_ids_by_gerente(gerente_id)
    #
    # def list_colaboradores_by_gerente(self, gerente_id: int) -> List[UserModel]:
    #     return self.user_repo.get_colaboradores_by_gerente(gerente_id)
    #
    # def list_colaboradores_by_time(self, time_id: int) -> List[UserModel]:
    #     return self.user_repo.get_colaboradores_by_time(time_id)

    def list_all_times(self):
        return self.time_repo.list_all()
