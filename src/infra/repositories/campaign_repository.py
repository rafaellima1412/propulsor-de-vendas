from sqlalchemy.orm import Session, joinedload

from src.application.dtos.campaign_create_dto import CampanhaCreateDTO
from src.application.repositories.icampaign_repository import ICampanhaRepository
from src.domain.entities.campaign import Campaign
from src.infra.database.models.user_model import UserModel
from src.infra.database.models.campaign_model import CampanhaModel


class CampanhaRepository(ICampanhaRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, campanha: CampanhaCreateDTO, usuario_id: int | None) -> Campaign:
        db_campanha = CampanhaModel(
            title=campanha.title,
            paragraph=campanha.paragraph,
            post_type=campanha.post_type,
            url=campanha.url,
            image=campanha.image,
            folder_url=campanha.folder_url,
            qrcode_url=campanha.qrcode_url,
            local_id=campanha.local_id,
        )

        if usuario_id is not None:
            usuario = self.db.query(UserModel).filter(UserModel.id == usuario_id).first()
            if not usuario:
                self.db.close()
                raise ValueError("Usuário não encontrado")

            db_campanha.usuarios.append(usuario)
        # sem usuario_id: campanha criada sem colaborador vinculado ainda —
        # associação acontece depois, pela tela de "associar campanha".

        self.db.add(db_campanha)
        self.db.commit()
        self.db.refresh(db_campanha)

        campaign = Campaign(
            id=db_campanha.id,
            title=db_campanha.title,
            paragraph=db_campanha.paragraph,
            post_type=db_campanha.post_type,
            url=db_campanha.url,
            image=db_campanha.image,
            folder_url=db_campanha.folder_url,
            qrcode_url=db_campanha.qrcode_url,
            data_criacao=db_campanha.data_criacao,
            usuario_id=usuario_id,
            coordenador_id=db_campanha.coordenador_id,
            local_id=db_campanha.local_id,
        )
        self.db.close()
        return campaign

    def list_by_usuario_id(self, usuario_id: int) -> list[Campaign]:
        campanhas_db = (
            self.db.query(CampanhaModel)
            .join(CampanhaModel.usuarios)
            .filter(UserModel.id == usuario_id)
            .options(joinedload(CampanhaModel.usuarios))
            .all()
        )
        campanhas = [
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
                usuario_id=usuario_id,
                coordenador_id=c.coordenador_id,
                local_id=c.local_id,
            )
            for c in campanhas_db
        ]
        self.db.close()
        return campanhas

    def get_by_id(self, campanha_id: int) -> Campaign | None:
        db_campanha = self.db.query(CampanhaModel).filter(CampanhaModel.id == campanha_id).first()
        if not db_campanha:
            self.db.close()
            return None

        campaign = Campaign(
            id=db_campanha.id,
            title=db_campanha.title,
            paragraph=db_campanha.paragraph,
            post_type=db_campanha.post_type,
            url=db_campanha.url,
            image=db_campanha.image,
            folder_url=db_campanha.folder_url,
            qrcode_url=db_campanha.qrcode_url,
            data_criacao=db_campanha.data_criacao,
            usuario_id=db_campanha.usuarios[0].id if db_campanha.usuarios else None,
            coordenador_id=db_campanha.coordenador_id,
            local_id=db_campanha.local_id,
        )
        self.db.close()
        return campaign

    def list_by_coordenador_id(self, coordenador_id: int) -> list[Campaign]:
        campanhas_db = (
            self.db.query(CampanhaModel)
            .filter(CampanhaModel.coordenador_id == coordenador_id)
            .options(joinedload(CampanhaModel.usuarios))
            .all()
        )
        campanhas = [
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
                usuario_id=c.usuarios[0].id if c.usuarios else None,
                coordenador_id=c.coordenador_id,
                local_id=c.local_id,
            )
            for c in campanhas_db
        ]
        self.db.close()
        return campanhas

    def get_all(self) -> list[Campaign]:
        campanhas_db = self.db.query(CampanhaModel).options(joinedload(CampanhaModel.usuarios)).all()
        campanhas = [
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
                usuario_id=c.usuarios[0].id if c.usuarios else None,
                coordenador_id=c.coordenador_id,
                local_id=c.local_id,
            )
            for c in campanhas_db
        ]
        self.db.close()
        return campanhas

    def adicionar_colaborador(self, campanha_id: int, usuario_id: int) -> Campaign | None:
        db_campanha = self.db.query(CampanhaModel).filter(CampanhaModel.id == campanha_id).first()
        if not db_campanha:
            self.db.close()
            return None

        usuario = self.db.query(UserModel).filter(UserModel.id == usuario_id).first()
        if not usuario:
            self.db.close()
            raise ValueError("Usuário não encontrado.")

        ja_associado = any(u.id == usuario_id for u in db_campanha.usuarios)
        if not ja_associado:
            db_campanha.usuarios.append(usuario)
            self.db.commit()
            self.db.refresh(db_campanha)

        campaign = Campaign(
            id=db_campanha.id,
            title=db_campanha.title,
            paragraph=db_campanha.paragraph,
            post_type=db_campanha.post_type,
            url=db_campanha.url,
            image=db_campanha.image,
            folder_url=db_campanha.folder_url,
            qrcode_url=db_campanha.qrcode_url,
            data_criacao=db_campanha.data_criacao,
            usuario_id=db_campanha.usuarios[0].id if db_campanha.usuarios else None,
            coordenador_id=db_campanha.coordenador_id,
            local_id=db_campanha.local_id,
        )
        self.db.close()
        return campaign

    def definir_coordenador(self, campanha_id: int, coordenador_id: int) -> Campaign | None:
        db_campanha = self.db.query(CampanhaModel).filter(CampanhaModel.id == campanha_id).first()
        if not db_campanha:
            self.db.close()
            return None

        coordenador = self.db.query(UserModel).filter(UserModel.id == coordenador_id).first()
        if not coordenador:
            self.db.close()
            raise ValueError("Coordenador não encontrado.")

        db_campanha.coordenador_id = coordenador_id
        self.db.commit()
        self.db.refresh(db_campanha)

        campaign = Campaign(
            id=db_campanha.id,
            title=db_campanha.title,
            paragraph=db_campanha.paragraph,
            post_type=db_campanha.post_type,
            url=db_campanha.url,
            image=db_campanha.image,
            folder_url=db_campanha.folder_url,
            qrcode_url=db_campanha.qrcode_url,
            data_criacao=db_campanha.data_criacao,
            usuario_id=db_campanha.usuarios[0].id if db_campanha.usuarios else None,
            coordenador_id=db_campanha.coordenador_id,
            local_id=db_campanha.local_id,
        )
        self.db.close()
        return campaign

    def update(self, campaign: Campaign) -> Campaign:
        db_campaign = self.db.query(CampanhaModel).get(campaign.id)
        if not db_campaign:
            raise Exception("Campanha não encontrada")

        db_campaign.title = campaign.title
        db_campaign.paragraph = campaign.paragraph
        db_campaign.post_type = campaign.post_type
        db_campaign.url = campaign.url
        db_campaign.folder_url = campaign.folder_url
        db_campaign.qrcode_url = campaign.qrcode_url
        db_campaign.image = campaign.image
        db_campaign.local_id = campaign.local_id

        self.db.commit()
        self.db.refresh(db_campaign)

        updated_campaign = Campaign(
            id=db_campaign.id,
            title=db_campaign.title,
            paragraph=db_campaign.paragraph,
            post_type=db_campaign.post_type,
            url=db_campaign.url,
            image=db_campaign.image,
            folder_url=db_campaign.folder_url,
            qrcode_url=db_campaign.qrcode_url,
            data_criacao=db_campaign.data_criacao,
            usuario_id=db_campaign.usuarios[0].id if db_campaign.usuarios else None,
            coordenador_id=db_campaign.coordenador_id,
            local_id=db_campaign.local_id,
        )
        self.db.close()
        return updated_campaign
