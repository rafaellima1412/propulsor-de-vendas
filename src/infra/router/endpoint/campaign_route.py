import calendar
import os
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Form, Request, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from config.settings import BASE_DIR
from src.application.auth.auth import get_current_user
from src.application.dtos.campaign_create_dto import CampanhaCreateDTO
from src.application.services.qr_code_generator import generate_folder_with_qr
from src.application.use_cases.create_campaign_usecase import CreateCampanhaUseCase
from src.application.use_cases.update_campaign_usecase import UpdateCampaignUseCase
from src.domain.enums.enums import PlanoInternet
from src.domain.validators.cpf_validator import validar_cpf
from src.infra.database.db import get_db
from src.infra.database.models import VendaModel
from src.infra.dy.container import Container
from src.infra.repositories.campaign_repository import CampanhaRepository

router = APIRouter(prefix="/campanhas")

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
def campaign_to_dict(campaign):
    return {
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
@router.get("/cadastro", response_class=HTMLResponse)
async def show_campaign_form(request: Request):
    return templates.TemplateResponse("campaign_create.html", {
        "request": request,
        "title": "",
        "paragraph": "",
        "cpf": "",
        "matricula": "",
        "errors": [],
    })

@router.get("/dashboard", response_class=HTMLResponse)
@inject
async def form_page(
        request: Request,
        user: dict = Depends(get_current_user),
        db: Session = Depends(get_db),
        campanha_repo: CampanhaRepository = Depends(Provide[Container.campanha_repository])
):
    campanhas = campanha_repo.list_by_usuario_id(user["id"])
    module = {
        "carousel_item": campanhas
    }

    resultados_plano = (
        db.query(VendaModel.area, func.count(VendaModel.id)).group_by(VendaModel.area)
        .filter(VendaModel.status == "vendido")
        .group_by(VendaModel.area)
        .all()
    )
    vendas_por_plano = {
        plano.value if isinstance(plano, PlanoInternet) else plano: count
        for plano, count in resultados_plano
    }
    resultados_por_mes = (
        db.query(
            extract('year', VendaModel.data_criacao).label("ano"),
            extract('month', VendaModel.data_criacao).label("mes"),
            func.count(VendaModel.id)
        )
        .filter(VendaModel.status == "vendido")
        .group_by("ano", "mes")
        .order_by("ano", "mes")
        .all()
    )
    mes_labels = [f"{calendar.month_abbr[int(mes)].capitalize()}/{int(ano)}" for ano, mes, _ in resultados_por_mes]
    mes_data = [count for _, _, count in resultados_por_mes]

    planos_labels = [plano for plano, _ in resultados_plano]
    planos_data = [count for _, count in resultados_plano]
    planos_cores = ['#3498db', '#2ecc71', '#f1c40f', '#e74c3c', '#9b59b6'][:len(planos_labels)]
    area_data = planos_data


    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "module": module,
        "area_colors": planos_cores,
        "planos_labels": planos_labels,
        "planos_data": planos_data,
        "planos_cores": planos_cores,
        "vendas_por_plano": vendas_por_plano,
        "area_labels": planos_labels,
        "area_data": area_data,
        "area_colors": planos_cores,
        "mes_labels": mes_labels,
        "mes_data": mes_data,
    })


@router.get("/view/{campaign_id}", response_class=HTMLResponse)
@inject
async def campaign_detail(
    request: Request,
    campaign_id: int,
    user: dict = Depends(get_current_user),
    campanha_repo: CampanhaRepository = Depends(Provide[Container.campanha_repository]),
):
    campaign = campanha_repo.get_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    if user["role"] not in ["colaborador", "gerente"]:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Acesso negado"},
            status_code=403,
        )
    template_name = "campaign_detail.html" if user["role"] == "colaborador" else "campaign_edit.html"

    return templates.TemplateResponse(template_name, {
        "request": request,
        "campaign": campaign,
        "user": user
    })

@router.post("/edit/{campaign_id}", response_class=HTMLResponse)
@inject
async def update_campaign(
    request: Request,
    campaign_id: int,
    title: str = Form(...),
    paragraph: str = Form(...),
    post_type: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    folder_url: Optional[str] = Form(None),
    qrcode_url: Optional[str] = Form(None),
    user: dict = Depends(get_current_user),
    use_case: UpdateCampaignUseCase = Depends(Provide[Container.update_campaign_use_case]),
):
    campaign = use_case.execute(
        user=user,
        campaign_id=campaign_id,
        title=title,
        paragraph=paragraph,
        post_type=post_type,
        url=url,
        folder_url=folder_url,
        qrcode_url=qrcode_url,
    )

    return templates.TemplateResponse("campaign_edit.html", {
        "request": request,
        "campaign": campaign,
        "user": user,
        "message": "Campanha atualizada com sucesso!"
    })

@router.post("/cadastro", response_class=HTMLResponse, response_model=None)
@inject
async def generate(
        request: Request,
        title: str = Form(...),
        paragraph: str = Form(...),
        cpf: str = Form(...),
        matricula: str = Form(...),
        post_type: Optional[str] = Form(None),
        url: Optional[str] = Form(None),
        folder_url: Optional[str] = Form(None),
        qrcode_url: Optional[str] = Form(None),
        folder_image: UploadFile = File(...),
    use_case: CreateCampanhaUseCase = Depends(Provide[Container.create_campaign_use_case])
):
    errors = []

    if not validar_cpf(cpf):
        errors.append("CPF inválido!")

    if not errors:
        output_filename = await generate_folder_with_qr(cpf, matricula, folder_image)
        output_url = f"/static/outputs/{output_filename}"
        try:
            data = CampanhaCreateDTO(
                title=title,
                paragraph=paragraph,
                cpf_usuario=cpf,
                image=output_url,
                url=url or "",
                post_type=post_type or "",
                folder_url=folder_url or "",
                qrcode_url=qrcode_url or ""
            )

            clean_data = {k: v for k, v in data.model_dump().items() if v is not None}
            dto = CampanhaCreateDTO(**clean_data)
            use_case.execute(dto)

            return RedirectResponse(url="/campanhas/dashboard", status_code=302)

        except ValueError as e:
            errors.append(str(e))

    return templates.TemplateResponse("campaign_create.html", {
        "request": request,
        "title": title,
        "paragraph": paragraph,
        "cpf": cpf,
        "matricula": matricula,
        "errors": errors
    })