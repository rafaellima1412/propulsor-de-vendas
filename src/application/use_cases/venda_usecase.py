from typing import List, Optional, Dict, Tuple
from src.application.dtos.venda_create_dto import VendaCreateDTO
from src.application.repositories.ivenda_repository import IVendaRepository
from src.infra.database.models.venda_model import VendaModel

class VendaUseCase:
    def __init__(self, repository: IVendaRepository):
        self.repository = repository

    def create_venda(self, venda: VendaCreateDTO) -> VendaModel:
        return self.repository.create(venda)

    def list_vendas(self) -> List[VendaModel]:
        return self.repository.get_all()

    def get_venda(self, venda_id: int) -> Optional[VendaModel]:
        return self.repository.get_by_id(venda_id)

    def vendas_por_plano(self, usuario_id: int) -> Dict[str, int]:
        return self.venda_repo.vendas_por_plano(usuario_id)

    def vendas_por_mes(self, usuario_id: int) -> Tuple[List[str], List[int]]:
        return self.venda_repo.vendas_por_mes(usuario_id)