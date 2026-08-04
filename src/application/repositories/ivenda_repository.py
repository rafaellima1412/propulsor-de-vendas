# application/interfaces/venda_repository_interface.py
from abc import ABC, abstractmethod

from src.application.dtos.venda_create_dto import VendaCreateDTO
from src.infra.database.models.venda_model import VendaModel


class IVendaRepository(ABC):
    @abstractmethod
    def create(self, venda: VendaCreateDTO) -> VendaModel:
        pass

    @abstractmethod
    def get_all(self) -> list[VendaModel]:
        pass

    @abstractmethod
    def get_by_id(self, venda_id: int) -> VendaModel | None:
        pass

    @abstractmethod
    def get_by_usuario_ids(self, usuario_ids: list[int]) -> list[VendaModel]:
        """Vendas feitas pelos colaboradores informados — usado pra restringir
        o gerente às vendas do próprio time (coordenador continua vendo tudo
        via get_all)."""
        pass

    @abstractmethod
    def contagem_por_plano(self,usuario_ids: int | list[int]) -> dict[str, int]:
        pass

    @abstractmethod
    def contagem_por_mes(self, usuario_ids: list[int]) -> dict[tuple[int, int], int]:
        pass

    @abstractmethod
    def contagem_por_plano_all(self) -> dict[str, int]:
        """Igual a contagem_por_plano, mas sem filtro de usuário — todas as vendas da empresa."""
        pass

    @abstractmethod
    def contagem_por_mes_all(self) -> dict[tuple[int, int], int]:
        """Igual a contagem_por_mes, mas sem filtro de usuário — todas as vendas da empresa."""
        pass