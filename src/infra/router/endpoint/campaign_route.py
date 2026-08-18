import mimetypes
import os
import uuid
from pathlib import Path

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image
from starlette import status

from config.settings import OUTPUT_FOLDER, UPLOAD_FOLDER
from src.application.auth.auth import get_current_user
from src.application.dtos.campaign_create_dto import CampanhaCreateDTO
from src.application.dtos.update_campaign_dto import UpdateCampaignDTO
from src.application.services.qr_code_generator import resolve_local_media_path
from src.application.use_cases.create_campaign_usecase import CreateCampanhaUseCase
from src.application.use_cases.dashboard_usecase import DashboardUseCase
from src.application.use_cases.team_usecase import TimeUseCase
from src.application.use_cases.update_campaign_usecase import UpdateCampaignUseCase
from src.application.use_cases.user_usecase import UserUseCase
from src.infra.dy.container import Container
from src.infra.repositories.campaign_repository import CampanhaRepository
from src.infra.router.schemas.campanha_requests import AssociarColaboradorRequest, AssociarCoordenadorRequest

router = APIRouter(prefix="/campanhas")

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

# Dimensões-alvo (px) de cada formato de post. "post" aqui é o formato
# horizontal genérico (ex: link preview / post de feed paisagem).
SOCIAL_FORMATS = {
    "feed": (1080, 1080),
    "stories": (1080, 1920),
    "post": (1080, 608),
}


def _fit_cover(image: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """Redimensiona a imagem pra cobrir totalmente o tamanho alvo (sem
    distorcer) e corta o excesso centralizado — igual ao `object-fit: cover`
    do CSS."""
    target_w, target_h = target_size
    src_w, src_h = image.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w, new_h = round(src_w * scale), round(src_h * scale)
    resized = image.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


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
    dashboard_usecase: DashboardUseCase = Depends(Provide[Container.dashboard_usecase]),
):
    resultado = dashboard_usecase.get_dashboard_data(user=user)

    return {
        "user": user,
        "campanhas": resultado["campanhas"],
        # "scope": resultado["scope"],
        "dashboard_data": resultado["dashboard_data"],
    }


@router.get("/de-usuario/{usuario_id}")
@inject
async def campanhas_de_usuario(
    usuario_id: int,
    user: dict = Depends(get_current_user),
    campanha_repo: CampanhaRepository = Depends(Provide[Container.campanha_repository]),
):
    """Campanhas de um colaborador específico — usado pra popular o
    seletor de campanha na tela de simular venda."""
    if user["role"] not in ("coordenador", "gerente"):
        raise HTTPException(status_code=403, detail="Acesso negado")

    campanhas = campanha_repo.list_by_usuario_id(usuario_id)
    return [campaign_to_dict(c) for c in campanhas]


@router.get("/do-time")
@inject
async def campanhas_do_time(
    user: dict = Depends(get_current_user),
    campanha_repo: CampanhaRepository = Depends(Provide[Container.campanha_repository]),
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    """Campanhas do time do usuário logado. Gerente vê o time que gerencia
    (pode ter mais de um); colaborador vê o time em que está."""
    if user["role"] == "coordenador":
        time_ids = user_usecase.list_times_by_gerente(user["id"])
        user_usecase.close()
    elif user["role"] == "colaborador":
        colaborador = user_usecase.get_user(user["id"])
        time_ids = [colaborador.time_id] if colaborador and colaborador.time_id else []
        user_usecase.close()
    else:
        raise HTTPException(status_code=403, detail="Acesso negado")

    campanhas = campanha_repo.list_by_time_ids(time_ids)
    return [campaign_to_dict(c) for c in campanhas]


@router.get("/de-gerente/{gerente_id}")
@inject
async def campanhas_de_gerente(
    gerente_id: int,
    user: dict = Depends(get_current_user),
    campanha_repo: CampanhaRepository = Depends(Provide[Container.campanha_repository]),
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    """Campanhas do time de um gerente específico — visão do coordenador."""
    if user["role"] != "gerente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    time_ids = user_usecase.list_times_by_gerente(gerente_id)
    user_usecase.close()

    campanhas = campanha_repo.list_by_time_ids(time_ids)
    return [campaign_to_dict(c) for c in campanhas]


@router.get("/sem-coordenador")
@inject
async def campanhas_sem_coordenador(
    user: dict = Depends(get_current_user),
    campanha_repo: CampanhaRepository = Depends(Provide[Container.campanha_repository]),
):
    """Campanhas que ainda não têm nenhum time (e portanto nenhum
    coordenador) vinculado. Usado na tela 'Campanhas por coordenador' pra
    escolher qual campanha vincular."""
    if user["role"] != "gerente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    campanhas = campanha_repo.get_all()
    sem_coordenador = [c for c in campanhas if not c.times]
    return [campaign_to_dict(c) for c in sem_coordenador]


@router.post("/{campanha_id}/colaboradores", status_code=status.HTTP_201_CREATED)
@inject
async def associar_colaborador(
    campanha_id: int,
    payload: AssociarColaboradorRequest,
    user: dict = Depends(get_current_user),
    campanha_repo: CampanhaRepository = Depends(Provide[Container.campanha_repository]),
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    """Associa um colaborador a uma campanha já existente (além de quem já
    estava). Gerente só pode associar colaboradores do próprio time (ou
    ainda sem time); coordenador pode associar qualquer um."""
    if user["role"] not in ("coordenador", "gerente"):
        raise HTTPException(status_code=403, detail="Acesso negado")

    colaborador = user_usecase.get_user(payload.usuario_id)
    if not colaborador or colaborador.role != "colaborador":
        user_usecase.close()
        raise HTTPException(status_code=400, detail="Colaborador não encontrado.")

    if user["role"] == "coordenador":
        time_ids_gerente = user_usecase.list_times_by_gerente(user["id"])
        if colaborador.time_id is not None and colaborador.time_id not in time_ids_gerente:
            user_usecase.close()
            raise HTTPException(status_code=403, detail="Esse colaborador não é do seu time.")
    user_usecase.close()

    try:
        campanha = campanha_repo.adicionar_colaborador(campanha_id, payload.usuario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada.")

    return campanha


@router.post("/{campanha_id}/coordenador", status_code=status.HTTP_201_CREATED)
@inject
async def associar_coordenador(
    campanha_id: int,
    payload: AssociarCoordenadorRequest,
    user: dict = Depends(get_current_user),
    campanha_repo: CampanhaRepository = Depends(Provide[Container.campanha_repository]),
    user_usecase: UserUseCase = Depends(Provide[Container.user_usecase]),
):
    """Vincula o(s) time(s) de um coordenador a uma campanha já existente
    (além dos que já estavam). Uso: tela 'Campanhas por coordenador'."""
    if user["role"] != "gerente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    coordenador = user_usecase.get_user(payload.coordenador_id)
    if not coordenador or coordenador.role != "coordenador":
        user_usecase.close()
        raise HTTPException(status_code=400, detail="Coordenador não encontrado.")

    time_ids = user_usecase.list_times_by_gerente(payload.coordenador_id)
    user_usecase.close()

    if not time_ids:
        raise HTTPException(status_code=400, detail="Esse coordenador ainda não tem nenhum time.")

    campanha = None
    try:
        for time_id in time_ids:
            campanha = campanha_repo.adicionar_time(campanha_id, time_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if not campanha:
        raise HTTPException(status_code=404, detail="Campanha não encontrada.")

    return campanha


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

    if user["role"] not in ["colaborador", "coordenador", "gerente"]:
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

@router.get("/{campaign_id}/social/{formato}")
@inject
async def campaign_social_image(
    campaign_id: int,
    formato: str,
    user: dict = Depends(get_current_user),
    campanha_repo: CampanhaRepository = Depends(Provide[Container.campanha_repository]),
):
    """Gera (e cacheia em disco) uma versão da imagem final da campanha
    recortada pro formato pedido — pra colaborador postar direto no Feed,
    Stories ou como post horizontal, sem precisar recortar na mão."""
    if formato not in SOCIAL_FORMATS:
        raise HTTPException(status_code=404, detail="Formato inválido. Use feed, stories ou post.")

    campaign = campanha_repo.get_by_id(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")

    # Colaborador só pode gerar recortes da própria campanha; gerente e
    # coordenador podem de qualquer uma (mesma regra do campaign_detail).
    if user["role"] == "colaborador":
        if campaign.usuario_id != user["id"]:
            raise HTTPException(status_code=403, detail="Acesso negado")
    elif user["role"] not in ("coordenador", "gerente"):
        raise HTTPException(status_code=403, detail="Acesso negado")

    if not campaign.image:
        raise HTTPException(status_code=404, detail="Essa campanha ainda não tem imagem gerada.")

    source_path = resolve_local_media_path(campaign.image)
    if source_path is None:
        raise HTTPException(status_code=404, detail="Imagem da campanha não encontrada em disco.")

    cache_dir = Path(OUTPUT_FOLDER) / "social"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{campaign_id}_{formato}.png"

    # Regenera só se ainda não existe ou se a imagem original mudou desde a
    # última vez (ex: campanha foi editada com uma imagem nova).
    if not cache_path.exists() or os.path.getmtime(source_path) > os.path.getmtime(cache_path):
        base_image = Image.open(source_path).convert("RGB")
        social_image = _fit_cover(base_image, SOCIAL_FORMATS[formato])
        social_image.save(cache_path)

    return FileResponse(cache_path, media_type="image/png", filename=f"{campaign.title}_{formato}.png")


@router.put("/{campaign_id}")
@inject
async def update_campaign(
    campaign_id: int,
    update_dto: UpdateCampaignDTO,
    user: dict = Depends(get_current_user),
    use_case: UpdateCampaignUseCase = Depends(Provide[Container.update_campaign_use_case]),
):
    campaign = await use_case.execute(user=user, campaign_id=campaign_id, update_dto=update_dto)

    return {"message": "Campanha atualizada com sucesso!", "campaign": campaign_to_dict(campaign)}

@router.post("/upload-imagem", status_code=status.HTTP_201_CREATED)
@inject
async def upload_imagem_base(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Recebe a imagem base (arte da campanha) escolhida no front, salva em
    media/uploads e devolve a URL pra ser usada como `folder_image` em
    POST /campanhas/. Não cria a campanha em si — é um passo separado."""
    if user["role"] != "gerente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    content_type = file.content_type or mimetypes.guess_type(file.filename or "")[0]
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400, detail="Formato inválido. Envie um arquivo JPEG, PNG ou WEBP."
        )

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="Imagem muito grande (máximo 10MB).")

    extensao = mimetypes.guess_extension(content_type) or Path(file.filename or "").suffix or ".jpg"
    nome_arquivo = f"{uuid.uuid4().hex}{extensao}"
    destino = Path(UPLOAD_FOLDER) / nome_arquivo
    destino.write_bytes(contents)

    return {"url": f"/media/uploads/{nome_arquivo}"}


@router.post("/", status_code=status.HTTP_201_CREATED)
@inject
async def create_campaign(
    payload: CampanhaCreateDTO,
    user: dict = Depends(get_current_user),
    use_case: CreateCampanhaUseCase = Depends(Provide[Container.create_campaign_use_case]),
):
    if user["role"] != "gerente":
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        dto = payload.model_copy(update={"image": payload.folder_image})
        campaign = use_case.execute(dto)
        return {"message": "Campanha criada com sucesso!", "campaign": campaign_to_dict(campaign)}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e