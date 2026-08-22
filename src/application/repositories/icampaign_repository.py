from abc import ABC, abstractmethod

from src.application.dtos.campaign_create_dto import CampanhaCreateDTO
from src.domain.entities.campaign import Campaign
from src.infra.database.models.campaign_model import CampanhaModel


class ICampanhaRepository(ABC):
    @abstractmethod
    def create(self, campanha: CampanhaCreateDTO, usuario_id: int | None) -> Campaign:
        pass

    @abstractmethod
    def list_by_usuario_id(self, usuario_id: int) -> list[Campaign]:
        pass

    @abstractmethod
    def list_by_coordenador_id(self, coordenador_id: int) -> list[Campaign]:
        pass

    @abstractmethod
    def update(self, campaign: Campaign) -> Campaign:
        pass

    @abstractmethod
    def get_by_id(self, campanha_id: int) -> CampanhaModel | None:
        pass

    @abstractmethod
    def get_detalhe(self, campanha_id: int) -> dict | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Campaign]:
        pass

    @abstractmethod
    def adicionar_colaborador(self, campanha_id: int, usuario_id: int) -> Campaign | None:
        pass

    @abstractmethod
    def definir_coordenador(self, campanha_id: int, coordenador_id: int) -> Campaign | None:
        pass
