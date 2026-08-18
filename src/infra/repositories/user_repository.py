from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from src.application.dtos.user_create_dto import UserCreateDTO
from src.application.repositories.iuser_repository import IUserRepository
from src.infra.database.models.campaign_model import CampanhaModel
from src.infra.database.models.user_model import UserModel


class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: UserCreateDTO):
        db_user = UserModel(
            username=user.username.strip(),
            full_name=user.full_name.strip(),
            cpf=user.cpf,
            role=user.role,
            hashed_password=user.hashed_password,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        self.db.close()
        return db_user

    def update(self, user: UserModel) -> UserModel:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        self.db.close()
        return user

    def get_all(self):
        resultado = self.db.query(UserModel).all()
        self.db.close()
        return resultado

    def get_by_username(self, username: str) -> UserModel | None:
        resultado = self.db.query(UserModel).filter(UserModel.username == username).first()
        self.db.close()
        return resultado

    def get_by_id(self, user_id: int) -> UserModel | None:
        resultado = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        self.db.close()
        return resultado

    def get_by_cpf(self, cpf: str) -> UserModel | None:
        resultado = self.db.query(UserModel).filter(UserModel.cpf == cpf).first()
        self.db.close()
        return resultado

    def get_by_role(self, role: str) -> list[UserModel]:
        resultado = (
            self.db.query(UserModel).options(selectinload(UserModel.campanhas)).filter(UserModel.role == role).all()
        )
        self.db.close()
        return resultado

    def get_colaboradores_by_coordenador(self, coordenador_id: int) -> list[UserModel]:
        """Colaboradores que estão em alguma campanha desse coordenador —
        não existe mais um 'time' fixo; o vínculo é via campanha."""
        resultado = (
            self.db.query(UserModel)
            .join(UserModel.campanhas)
            .filter(CampanhaModel.coordenador_id == coordenador_id)
            .distinct()
            .all()
        )
        self.db.close()
        return resultado

    def search_colaboradores(self, query: str | None = None) -> list[UserModel]:
        # ATENÇÃO: não fechar a sessão aqui — mesmo motivo do get_by_role
        # (serialização via UserOut faz lazy-load de `campanhas` logo em
        # seguida). Quem chama fecha depois (ver user_usecase.close()).
        base = self.db.query(UserModel).filter(UserModel.role == "colaborador")

        if query:
            termo = f"%{query.strip()}%"
            base = base.filter(
                or_(
                    UserModel.full_name.ilike(termo),
                    UserModel.cpf.ilike(termo),
                )
            )

        return base.order_by(UserModel.full_name).limit(50).all()
