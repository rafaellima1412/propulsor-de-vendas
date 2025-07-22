from abc import ABC, abstractmethod
from typing import List

from src.application.dtos.carteira_financeira_dto import CarteiraFinanceiraDTO


class ICarteiraRepository(ABC):

    @abstractmethod
    def list_carteira_by_usuario_id(self, usuario_id: int) -> List[CarteiraFinanceiraDTO]:
        """Retorna todos os itens da carteira financeira pertencentes ao usuário."""
        pass