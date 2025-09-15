# application/interfaces/venda_repository_interface.py
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict
from src.application.dtos.venda_create_dto import VendaCreateDTO
from src.infra.database.models.venda_model import VendaModel

class IVendaRepository(ABC):

    @abstractmethod
    def create(self, venda: VendaCreateDTO) -> VendaModel:
        pass

    @abstractmethod
    def get_all(self) -> List[VendaModel]:
        pass

    @abstractmethod
    def get_by_id(self, venda_id: int) -> Optional[VendaModel]:
        pass

    @abstractmethod
    def list_vendas_by_usuario_id(self, usuario_id: int) -> List[VendaModel]:
        """Retorna todas as vendas pertencentes ao usuário."""
        pass

    @abstractmethod
    def contagem_por_plano(self, user_id: int) -> Dict[str, int]:
        pass

    @abstractmethod
    def contagem_por_mes(self, user_id: int) -> Dict[Tuple[int, int], int]:
        pass