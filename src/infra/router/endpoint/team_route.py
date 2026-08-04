# src/infra/router/endpoint/time_router.py

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from src.application.auth.auth import get_current_user
from src.application.use_cases.team_usecase import TimeUseCase
from src.domain.entities.time_schema import TimeCreate, TimeOut
from src.infra.dy.container import Container

router = APIRouter(prefix="/times", tags=["Times"])


def require_coordenador(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "coordenador":
        raise HTTPException(status_code=403, detail="Acesso negado")
    return user


def require_gerente_ou_coordenador(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] not in ("gerente", "coordenador", "admin"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    return user


@router.get("/list", response_model=list[TimeOut])
@inject
async def list_times(
    user: dict = Depends(require_gerente_ou_coordenador),
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    return time_usecase.list_all()


@router.get("/{time_id}", response_model=TimeOut)
@inject
async def get_time(
    time_id: int,
    user: dict = Depends(require_gerente_ou_coordenador),
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    time = time_usecase.get_time_by_id(time_id)
    if not time:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    return time


@router.post("/create", response_model=TimeOut)
@inject
async def create_time(
    data: TimeCreate,
    user: dict = Depends(require_coordenador),
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    return  time_usecase.create_time(data)


@router.put("/{time_id}", response_model=TimeOut)
@inject
async def update_time(
    time_id: int,
    data: TimeCreate,
    user: dict = Depends(require_coordenador),
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    return await time_usecase.update_time(time_id, data)


@router.delete("/{time_id}")
@inject
async def delete_time(
    time_id: int,
    user: dict = Depends(require_coordenador),
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    await time_usecase.delete_time(time_id)
    return {"message": "Time deletado com sucesso"}


@router.get("/by-coo/{coo_id}", response_model=list[TimeOut])
@inject
async def get_times_by_coo(
    coo_id: int,
    user: dict = Depends(require_gerente_ou_coordenador),
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    return  time_usecase.get_times_by_coo(coo_id)


@router.get("/by-gerente/{gerente_id}", response_model=list[TimeOut])
@inject
async def get_times_by_gerente(
    gerente_id: int,
    user: dict = Depends(require_gerente_ou_coordenador),
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    return  time_usecase.get_times_by_gerente(gerente_id)