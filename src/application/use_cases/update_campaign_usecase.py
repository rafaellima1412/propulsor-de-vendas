from fastapi import HTTPException

from src.application.dtos.update_campaign_dto import UpdateCampaignDTO
from src.application.repositories.icampaign_repository import ICampanhaRepository
from src.application.repositories.iuser_repository import IUserRepository
from src.domain.entities.campaign import Campaign


class UpdateCampaignUseCase:
    def __init__(self, campanha_repo: ICampanhaRepository, user_repo: IUserRepository):
        self._campanha_repo = campanha_repo
        self._user_repo = user_repo

    async def execute(
        self,
        user: dict,
        campaign_id: int,
        update_dto: UpdateCampaignDTO,
    ) -> Campaign:
        campaign = self._campanha_repo.get_by_id(campaign_id)

        if not campaign:
            raise HTTPException(status_code=404, detail="Campanha não encontrada")

        if user["role"] not in ["coordenador", "gerente"]:  # somente coordenador e gerente pode editar campanha
            raise HTTPException(status_code=403, detail="Acesso negado")

        campaign.title = update_dto.title
        campaign.paragraph = update_dto.paragraph
        campaign.post_type = update_dto.post_type
        campaign.url = update_dto.url
        campaign.folder_url = update_dto.folder_url
        campaign.qrcode_url = update_dto.qrcode_url

        if update_dto.folder_image:
            campaign.image = update_dto.folder_image

        return self._campanha_repo.update(campaign)
