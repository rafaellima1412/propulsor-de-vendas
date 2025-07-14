from src.application.dtos.campaign_create_dto import CampanhaCreateDTO
from src.application.repositories.icampaign_repository import ICampanhaRepository
from src.application.repositories.iuser_repository import IUserRepository
from src.domain.entities.campaign import Campaign


class CreateCampanhaUseCase:
    def __init__(self, campanha_repo: ICampanhaRepository, user_repo: IUserRepository):
        self._campanha_repo = campanha_repo
        self._user_repo = user_repo

    def execute(self, dto: CampanhaCreateDTO) -> Campaign:
        usuario = self._user_repo.get_by_cpf(dto.cpf_usuario)
        if not usuario:
            raise ValueError("Usuário com CPF informado não encontrado.")

        return self._campanha_repo.create(dto, usuario.id)

