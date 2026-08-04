from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from src.application.auth.auth import get_current_user
from src.application.use_cases.carteira_usecases import CarteiraUseCase
from src.domain.entities.carteira_schema import CarteiraOut
from src.infra.dy.container import Container

router = APIRouter(prefix="/carteira")


@router.get("/me", response_model=CarteiraOut)
@inject
async def minha_carteira(
    user: dict = Depends(get_current_user),
    usecase: CarteiraUseCase = Depends(Provide[Container.carteira_usecase]),
):
    """Resultado e esforço do próprio usuário logado — pensado pro
    colaborador acompanhar as vendas geradas pelas campanhas dele."""
    return usecase.calcular_carteira(user["id"])


@router.get("/{usuario_id}", response_model=CarteiraOut)
@inject
async def carteira_de_usuario(
    usuario_id: int,
    user: dict = Depends(get_current_user),
    usecase: CarteiraUseCase = Depends(Provide[Container.carteira_usecase]),
):
    if user["role"] not in ("gerente", "coordenador"):
        raise HTTPException(status_code=403, detail="Acesso negado")

    return usecase.calcular_carteira(usuario_id)