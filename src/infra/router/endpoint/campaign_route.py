from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from starlette import status

from src.application.auth.auth import get_current_user
from src.application.dtos.campaign_create_dto import CampanhaCreateDTO
from src.application.dtos.update_campaign_dto import UpdateCampaignDTO
from src.application.services.qr_code_generator import generate_folder_with_qr
from src.application.use_cases.create_campaign_usecase import CreateCampanhaUseCase
from src.application.use_cases.dashboard_usecase import DashboardUseCase
from src.application.use_cases.team_usecase import TimeUseCase
from src.application.use_cases.update_campaign_usecase import UpdateCampaignUseCase
from src.domain.validators.cpf_validator import validar_cpf
from src.infra.database.db import get_db
from src.infra.database.models.user_model import UserModel
from src.infra.dy.container import Container
from src.infra.repositories.campaign_repository import CampanhaRepository

router = APIRouter(prefix="/campanhas")


def campaign_to_dict(campaign):
    return {
        "id": campaign.id,
        "title": campaign.title,
        "paragraph": campaign.paragraph,
        "post_type": campaign.post_type,
        "url": campaign.url,
        "image": campaign.image,
        "folder_url": campaign.folder_url,
        "qrcode_url": campaign.qrcode_url,
        "usuario_id": campaign.usuario_id,
        "data_criacao": campaign.data_criacao.strftime("%Y-%m-%d %H:%M:%S") if campaign.data_criacao else None,
    }


@router.get("/by-usuario")
@inject
async def dashboard(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    dashboard_usecase: DashboardUseCase = Depends(Provide[Container.dashboard_usecase]),
):
    """Dados do dashboard do usuário logado (campanhas, indicadores, planos)."""
    time_id = db.query(UserModel.time_id).filter(UserModel.id == user["id"]).scalar()

    resultado = dashboard_usecase.get_dashboard_data(user_id=user["id"], time_id=time_id)

    return {
        "user": user,
        "campanhas": resultado["campanhas"],
        "dashboard_data": resultado["dashboard_data"],
        "planos_cores": resultado["planos_cores"],
    }


@router.get("/{campaign_id}")
@inject
async def campaign_detail(
    campaign_id: int,
    user: dict = Depends(get_current_user),
    campanha_repo: CampanhaRepository = Depends(Provide[Container.campanha_repository]),
    time_usecase: TimeUseCase = Depends(Provide[Container.time_usecase]),
):
    campaign = campanha_repo.get_by_id(campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")

    if user["role"] not in ["colaborador", "gerente", "coo"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    # O frontend decide, com base em user.role, se mostra a tela de detalhe
    # (colaborador) ou a tela de edição (gerente/coo) — antes isso escolhia
    # o template no backend, agora é decisão de UI.
    user_times = time_usecase.get_times_by_user(user["id"])

    return {
        "campaign": campaign_to_dict(campaign),
        "user": user,
        "times": user_times,
        "editable": user["role"] != "colaborador",
    }

@router.put("/{campaign_id}")
@inject
async def update_campaign(
    campaign_id: int,
    update_dto: UpdateCampaignDTO,
    user: dict = Depends(get_current_user),
    use_case: UpdateCampaignUseCase = Depends(Provide[Container.update_campaign_use_case]),
):
    campaign = use_case.execute(user=user, campaign_id=campaign_id, update_dto=update_dto)

    return {"message": "Campanha atualizada com sucesso!", "campaign": campaign_to_dict(campaign)}

@router.post("/", status_code=status.HTTP_201_CREATED)
@inject
async def create_campaign(
    title: str = Form(...),
    paragraph: str = Form(...),
    cpf: str = Form(...),
    matricula: str = Form(...),
    post_type: str | None = Form(None),
    url: str | None = Form(None),
    folder_url: str | None = Form(None),
    qrcode_url: str | None = Form(None),
    folder_image: UploadFile = File(...),
    use_case: CreateCampanhaUseCase = Depends(Provide[Container.create_campaign_use_case]),
):
    if not validar_cpf(cpf):
        raise HTTPException(status_code=400, detail="CPF inválido!")

    try:
        output_filename = await generate_folder_with_qr(cpf, matricula, folder_image)
        output_url = f"/media/outputs/{output_filename}"
        data = CampanhaCreateDTO(
            title=title,
            paragraph=paragraph,
            cpf_usuario=cpf,
            image=output_url,
            url=url or "",
            post_type=post_type or "",
            folder_url=folder_url or "",
            qrcode_url=qrcode_url or "",
        )
        clean_data = {k: v for k, v in data.model_dump().items() if v is not None}
        dto = CampanhaCreateDTO(**clean_data)
        campaign = use_case.execute(dto)
        return {"message": "Campanha criada com sucesso!", "campaign": campaign_to_dict(campaign)}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
