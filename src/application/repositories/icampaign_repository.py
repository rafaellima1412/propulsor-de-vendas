from abc import ABC, abstractmethod
from typing import Optional

from src.application.dtos.campaign_create_dto import CampanhaCreateDTO
from src.domain.entities.campaign import Campaign
from src.infra.database.models.campaign_model  import CampanhaModel
from src.infra.database.models.time_model import TimeModel


class ICampanhaRepository(ABC):
    @abstractmethod
    def create(self, campanha: CampanhaCreateDTO, usuario_id: int | None) -> Campaign:
        pass

    @abstractmethod
    def list_by_usuario_id(self, usuario_id: int) -> list[Campaign]:
        pass

    @abstractmethod
    def list_by_time_ids(self, time_ids: list[int]) -> list[Campaign]:
        pass

    @abstractmethod
    def update(self, campaign: Campaign) -> Campaign:
        pass

    @abstractmethod
    def get_time_by_id(self, time_id: int) -> Optional[TimeModel]:
        pass

    @abstractmethod
    def get_by_id(self, campanha_id: int) -> CampanhaModel | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Campaign]:
        pass

    @abstractmethod
    def adicionar_colaborador(self, campanha_id: int, usuario_id: int) -> Campaign | None:
        pass

    @abstractmethod
    def adicionar_time(self, campanha_id: int, time_id: int) -> Campaign | None:
        pass