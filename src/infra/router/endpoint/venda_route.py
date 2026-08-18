from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from src.application.auth.auth import get_current_user
from src.application.dtos.venda_create_dto import VendaCreateDTO
from src.application.use_cases.user_usecase import UserUseCase
from src.application.use_cases.venda_usecase import VendaUseCase
from src.domain.entities.venda_schema import VendaOut
from src.infra.dy.container import Container

router = APIRouter(prefix="/vendas")


def require_gerente_ou_coordenador(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] not in ("coordenador", "gerente"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    return user


@router.post("/", response_model=VendaOut, status_code=201)
@inject
def create_venda(
    venda: VendaCreateDTO,
    user: dict = Depends(require_gerente_ou_coordenador),
    usecase: VendaUseCase = Depends(Provide[Container.venda_usecase]),
):
    return usecase.create_venda(venda)


@router.get("/", response_model=list[VendaOut])
@inject
def list_vendas(
    user: dict = Depends(require_gerente_ou_coordenador),
    usecase: VendaUseCase = Depends(Provide[Container.venda_usecase]),
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    # Coordenador vê tudo. Gerente vê só as vendas dos colaboradores do
    # próprio time — mesma regra de escopo já usada no dashboard.
    if user["role"] == "gerente":
        return usecase.list_vendas()

    colaboradores = user_usecase.list_colaboradores_by_coordenador(user["id"])
    colaborador_ids = [c.id for c in colaboradores]
    return usecase.list_vendas_by_usuario_ids(colaborador_ids)