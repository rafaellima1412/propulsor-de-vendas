from abc import ABC, abstractmethod
from typing import List, Optional

from src.application.dtos.campaign_create_dto import CampanhaCreateDTO
from src.domain.entities.campaign import Campaign
from src.infra.database.models import CampanhaModel


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

    @abstractmethod
    def get_time_by_id(self, time_id: int) -> Optional["TimeModel"]:
        pass

    @abstractmethod
    def get_by_id(self, campanha_id: int) -> Optional[CampanhaModel]:
        pass