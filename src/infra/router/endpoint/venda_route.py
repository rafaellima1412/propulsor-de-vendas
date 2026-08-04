from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from src.application.auth.auth import get_current_user
from src.application.dtos.venda_create_dto import VendaCreateDTO
from src.application.use_cases.venda_usecase import VendaUseCase
from src.infra.dy.container import Container

router = APIRouter(prefix="/vendas")


def require_gerente_ou_coordenador(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] not in ("gerente", "coordenador"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    return user


@router.post("/")
@inject
def create_venda(
    venda: VendaCreateDTO,
    user: dict = Depends(require_gerente_ou_coordenador),
    usecase: VendaUseCase = Depends(Provide[Container.venda_usecase]),
):
    return usecase.create_venda(venda)


@router.get("/")
@inject
def list_vendas(
    user: dict = Depends(require_gerente_ou_coordenador),
    usecase: VendaUseCase = Depends(Provide[Container.venda_usecase]),
):
    return usecase.list_vendas()