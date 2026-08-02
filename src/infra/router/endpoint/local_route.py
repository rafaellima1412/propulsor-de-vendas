from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from src.application.use_cases.local_usecase import LocalUseCase
from src.domain.entities.local_schema import LocalCreate, LocalSchema, LocalUpdate
from src.infra.dy.container import Container

router = APIRouter(prefix="/locais", tags=["Locais"])


@router.get("/", response_model=list[LocalSchema])
@inject
async def list_locais(
    local_usecase: LocalUseCase = Depends(Provide[Container.local_usecase]),
):
    return local_usecase.list_all()


@router.get("/{local_id}", response_model=LocalSchema)
@inject
async def get_local(
    local_id: int,
    local_usecase: LocalUseCase = Depends(Provide[Container.local_usecase]),
):
    local = local_usecase.get_by_id(local_id)
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return local


@router.post("/", response_model=LocalSchema, status_code=status.HTTP_201_CREATED)
@inject
async def create_local(
    data: LocalCreate,
    local_usecase: LocalUseCase = Depends(Provide[Container.local_usecase]),
):
    return local_usecase.create(data)


@router.put("/{local_id}", response_model=LocalSchema)
@inject
async def update_local(
    local_id: int,
    data: LocalUpdate,
    local_usecase: LocalUseCase = Depends(Provide[Container.local_usecase]),
):
    local = local_usecase.update(local_id, data)
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return local


@router.delete("/{local_id}")
@inject
async def delete_local(
    local_id: int,
    local_usecase: LocalUseCase = Depends(Provide[Container.local_usecase]),
):
    local = local_usecase.get_by_id(local_id)
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")

    local_usecase.delete(local_id)
    return {"message": "Local deletado com sucesso"}
