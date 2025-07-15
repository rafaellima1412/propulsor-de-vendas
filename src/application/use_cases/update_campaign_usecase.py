from typing import Optional

from fastapi import HTTPException

from src.application.repositories.icampaign_repository import ICampanhaRepository
from src.domain.entities.campaign import Campaign


class UpdateCampaignUseCase:
    def __init__(self, campanha_repo: ICampanhaRepository):
        self._campanha_repo = campanha_repo

    def execute(
        self,
        user: dict,
        campaign_id: int,
        title: str,
        paragraph: str,
        post_type: Optional[str],
        url: Optional[str],
        folder_url: Optional[str],
        qrcode_url: Optional[str],
    ) -> Campaign:
        campaign = self._campanha_repo.get_by_id(campaign_id)

        if not campaign:
            raise HTTPException(status_code=404, detail="Campanha não encontrada")

        if user["role"] not in ["colaborador", "gerente"]:
            raise HTTPException(status_code=403, detail="Acesso negado")

        campaign.title = title
        campaign.paragraph = paragraph
        campaign.post_type = post_type
        campaign.url = url
        campaign.folder_url = folder_url
        campaign.qrcode_url = qrcode_url

        self._campanha_repo.update(campaign)

        return campaign
