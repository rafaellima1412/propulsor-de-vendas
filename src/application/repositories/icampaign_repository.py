from abc import ABC, abstractmethod
from typing import List

from src.application.dtos.campaign_create_dto import CampanhaCreateDTO
from src.domain.entities.campaign import Campaign


class ICampanhaRepository(ABC):
    @abstractmethod
    def create(self, campanha: CampanhaCreateDTO, usuario_id: int) -> Campaign:
        pass
    @abstractmethod
    def list_by_usuario_id(self, usuario_id: int) -> List[Campaign]:
        pass

    @abstractmethod
    def update(self, campaign: Campaign) -> None:
        pass