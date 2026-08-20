from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from src.application.auth.auth import get_current_user
from src.application.use_cases.carteira_usecase import CarteiraUseCase
from src.domain.entities.carteira_schema import (
    CarteiraAgregadaOut,
    CarteiraOut,
    MapaCalorPontoOut,
    RankingVendedorOut,
)
from src.infra.dy.container import Container

router = APIRouter(prefix="/carteira")


@router.get("/me", response_model=CarteiraOut)
@inject
async def minha_carteira(
    user: dict = Depends(get_current_user),
    usecase: CarteiraUseCase = Depends(Provide[Container.carteira_usecase]),
):

    return usecase.calcular_carteira(user["id"])


@router.get("/time", response_model=CarteiraAgregadaOut)
@inject
async def carteira_do_time(
    user: dict = Depends(get_current_user),
    usecase: CarteiraUseCase = Depends(Provide[Container.carteira_usecase]),
):

    if user["role"] != "coordenador":
        raise HTTPException(status_code=403, detail="Acesso negado")

    return usecase.calcular_carteira_time(user["id"])


@router.get("/geral", response_model=CarteiraAgregadaOut)
@inject
async def carteira_geral(
    user: dict = Depends(get_current_user),
    usecase: CarteiraUseCase = Depends(Provide[Container.carteira_usecase]),
):

    if user["role"] != "gerente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    return usecase.calcular_carteira_geral()


@router.get("/ranking/time", response_model=list[RankingVendedorOut])
@inject
async def ranking_time(
    user: dict = Depends(get_current_user),
    usecase: CarteiraUseCase = Depends(Provide[Container.carteira_usecase]),
):
    if user["role"] != "coordenador":
        raise HTTPException(status_code=403, detail="Acesso negado")

    return usecase.ranking_time(user["id"])


@router.get("/ranking/geral", response_model=list[RankingVendedorOut])
@inject
async def ranking_geral(
    user: dict = Depends(get_current_user),
    usecase: CarteiraUseCase = Depends(Provide[Container.carteira_usecase]),
):
    if user["role"] != "gerente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    return usecase.ranking_geral()


@router.get("/mapa-vendas/time", response_model=list[MapaCalorPontoOut])
@inject
async def mapa_vendas_time(
    user: dict = Depends(get_current_user),
    usecase: CarteiraUseCase = Depends(Provide[Container.carteira_usecase]),
):
    if user["role"] != "coordenador":
        raise HTTPException(status_code=403, detail="Acesso negado")

    return usecase.mapa_calor_time(user["id"])


@router.get("/mapa-vendas/geral", response_model=list[MapaCalorPontoOut])
@inject
async def mapa_vendas_geral(
    user: dict = Depends(get_current_user),
    usecase: CarteiraUseCase = Depends(Provide[Container.carteira_usecase]),
):
    if user["role"] != "gerente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    return usecase.mapa_calor_geral()


@router.get("/{usuario_id}", response_model=CarteiraOut)
@inject
async def carteira_de_usuario(
    usuario_id: int,
    user: dict = Depends(get_current_user),
    usecase: CarteiraUseCase = Depends(Provide[Container.carteira_usecase]),
):

    if user["role"] not in ("coordenador", "gerente"):
        raise HTTPException(status_code=403, detail="Acesso negado")

    return usecase.calcular_carteira(usuario_id)