# src/infra/router/endpoint/time_router.py
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.infra.dy.container import Container
from src.application.use_cases.team_usecase import TimeUseCase
from src.domain.entities.time_schema import TimeOut, TimeCreate

router = APIRouter(prefix="/times", tags=["Times"])

@router.get("/list", response_model=List[TimeOut])
@inject
async def list_times(
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    return time_usecase.list_all()


@router.get("/{time_id}", response_model=TimeOut)
@inject
async def get_time(
    time_id: int,
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
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    return await time_usecase.create_time(data)


@router.put("/{time_id}", response_model=TimeOut)
@inject
async def update_time(
    time_id: int,
    data: TimeCreate,
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    return await time_usecase.update_time(time_id, data)


@router.delete("/{time_id}")
@inject
async def delete_time(
    time_id: int,
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    await time_usecase.delete_time(time_id)
    return {"message": "Time deletado com sucesso"}


@router.get("/by-coo/{coo_id}", response_model=List[TimeOut])
@inject
async def get_times_by_coo(
    coo_id: int,
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    return await time_usecase.get_times_by_coo(coo_id)


@router.get("/by-gerente/{gerente_id}", response_model=List[TimeOut])
@inject
async def get_times_by_gerente(
    gerente_id: int,
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    return await time_usecase.get_times_by_gerente(gerente_id)