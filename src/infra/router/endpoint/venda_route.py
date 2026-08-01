from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.application.dtos.venda_create_dto import VendaCreateDTO
from src.application.use_cases.venda_usecase import VendaUseCase
from src.infra.dy.container import Container

router = APIRouter(prefix="/vendas")


@router.post("/")
@inject
def create_venda(
    venda: VendaCreateDTO,
    usecase: VendaUseCase = Depends(Provide[Container.venda_usecase]),
):
    return usecase.create_venda(venda)


@router.get("/")
@inject
def list_vendas(usecase: VendaUseCase = Depends(Provide[Container.venda_usecase])):
    return usecase.list_vendas()
