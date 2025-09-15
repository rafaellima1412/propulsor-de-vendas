from typing import List

from src.application.repositories.icampaign_repository import ICampanhaRepository
from src.domain.entities.campaign import Campaign


class CampanhaUseCase:
    def __init__(self, campanha_repo: ICampanhaRepository):
        self.campanha_repo = campanha_repo

    def list_by_usuario_id(self, usuario_id: int) -> List[Campaign]:
        return self.campanha_repo.list_by_usuario_id(usuario_id)

