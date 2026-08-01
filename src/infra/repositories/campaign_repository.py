from typing import Any

from sqlalchemy.orm import Session, joinedload

from src.application.dtos.campaign_create_dto import CampanhaCreateDTO
from src.application.dtos.update_campaign_dto import UpdateCampaignDTO
from src.application.repositories.icampaign_repository import ICampanhaRepository
from src.domain.entities.campaign import Campaign
from src.infra.database.models.user_model import UserModel
from src.infra.database.models.campaign_model import CampanhaModel
from src.infra.database.models.time_model import TimeModel


class CampanhaRepository(ICampanhaRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, campanha: CampanhaCreateDTO, usuario_id: int) -> Campaign:
        db_campanha = CampanhaModel(
            title=campanha.title,
            paragraph=campanha.paragraph,
            post_type=campanha.post_type,
            url=campanha.url,
            image=campanha.image,
            folder_url=campanha.folder_url,
            qrcode_url=campanha.qrcode_url,
        )
        usuario = self.db.query(UserModel).filter(UserModel.id == usuario_id).first()
        if not usuario:
            raise ValueError("Usuário não encontrado")

        db_campanha.usuarios.append(usuario)

        if usuario.time_id:
            time = self.db.query(TimeModel).filter(TimeModel.id == usuario.time_id).first()
            if time:
                db_campanha.times.append(time)
            else:
                raise ValueError("Time não encontrado")
        else:
            raise ValueError("Usuário não está associado a nenhum time")

        self.db.add(db_campanha)
        self.db.commit()
        self.db.refresh(db_campanha)

        campaign = Campaign.from_orm(db_campanha)
        self.db.close()
        return campaign

        # return Campaign(
        #     id=db_campanha.id,
        #     title=db_campanha.title,
        #     paragraph=db_campanha.paragraph,
        #     post_type=db_campanha.post_type,
        #     url=db_campanha.url,
        #     image=db_campanha.image,
        #     folder_url=db_campanha.folder_url,
        #     qrcode_url=db_campanha.qrcode_url,
        #     data_criacao=db_campanha.data_criacao
        # )

    def list_by_usuario_id(self, usuario_id: int) -> list[Campaign]:
        campanhas_db = (
            self.db.query(CampanhaModel)
            .join(CampanhaModel.usuarios)
            .filter(UserModel.id == usuario_id)
            .options(joinedload(CampanhaModel.usuarios))
            .all()
        )
        return [
            Campaign(
                id=c.id,
                title=c.title,
                paragraph=c.paragraph,
                post_type=c.post_type,
                url=c.url,
                image=c.image,
                folder_url=c.folder_url,
                qrcode_url=c.qrcode_url,
                data_criacao=c.data_criacao,
            )
            for c in campanhas_db
        ]

    def get_by_id(self, campanha_id: int) -> Campaign | None:
        db_campanha = self.db.query(CampanhaModel).filter(CampanhaModel.id == campanha_id).first()
        if not db_campanha:
            return None

        return Campaign(
            id=db_campanha.id,
            title=db_campanha.title,
            paragraph=db_campanha.paragraph,
            post_type=db_campanha.post_type,
            url=db_campanha.url,
            image=db_campanha.image,
            folder_url=db_campanha.folder_url,
            qrcode_url=db_campanha.qrcode_url,
            data_criacao=db_campanha.data_criacao,
            times=[time.id for time in db_campanha.times],
        )

    def list_by_time_id(self, time_id: int) -> list[Any] | list[type[CampanhaModel]]:
        if not time_id:
            return []

        return self.db.query(CampanhaModel).join(CampanhaModel.times).filter(TimeModel.id == time_id).all()

    def get_time_by_id(self, time_id: int) -> TimeModel | None:
        return self.db.query(TimeModel).filter(TimeModel.id == time_id).first()

    def update(self, campaign: UpdateCampaignDTO, usuario_id: int) -> Campaign:
        db_campaign = self.db.query(CampanhaModel).get(campaign.id)
        if not db_campaign:
            raise Exception("Campanha não encontrada")

        db_campaign.title = campaign.title
        db_campaign.paragraph = campaign.paragraph
        # db_campaign.post_type = campaign.post_type
        # db_campaign.url = campaign.url
        # db_campaign.folder_url = campaign.folder_url
        # db_campaign.qrcode_url = campaign.qrcode_url
        # self.db.commit()

        usuario = self.db.query(UserModel).filter(UserModel.id == usuario_id).first()
        if not usuario:
            raise ValueError("Usuário não encontrado")

        if usuario.time_id:
            time = self.db.query(TimeModel).filter(TimeModel.id == usuario.time_id).first()
            if not time:
                raise ValueError("Time não encontrado")

            # Substitui todos os times relacionados pela nova associação
            db_campaign.times = [time]

        self.db.commit()
        self.db.refresh(db_campaign)

        campaign = Campaign.from_orm(db_campaign)
        self.db.close()
        return campaign
