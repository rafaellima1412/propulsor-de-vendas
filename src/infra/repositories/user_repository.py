from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from src.application.dtos.user_create_dto import UserCreateDTO
from src.application.repositories.iuser_repository import IUserRepository
from src.infra.database.models.time_model import TimeModel
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
        # ATENÇÃO: não fechar a sessão aqui. assign_time() busca o usuário,
        # muda o time_id e chama update() em seguida NO MESMO objeto —
        # update() faz self.db.refresh(user), que exige uma sessão ativa.
        # Fechar aqui quebra esse fluxo com DetachedInstanceError (testado).
        # Quem usa get_by_id sem chamar update() depois deve fechar a
        # própria sessão manualmente (ver os outros call sites).
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_by_cpf(self, cpf: str) -> UserModel | None:
        resultado = self.db.query(UserModel).filter(UserModel.cpf == cpf).first()
        self.db.close()
        return resultado

    def get_by_role(self, role: str) -> list[UserModel]:
        # ATENÇÃO: não fechar a sessão aqui. Quem chama isso (rotas /gerentes
        # e usos futuros parecidos) serializa o resultado via UserOut logo em
        # seguida, o que pode disparar lazy-load em campanha.times (só
        # campanhas em si vêm eager-loaded, o nível de baixo não) — fechar
        # cedo quebraria isso. O chamador é responsável por fechar depois de
        # terminar de usar (ver user_usecase.close() nas rotas que usam isso).
        return self.db.query(UserModel).options(selectinload(UserModel.campanhas)).filter(UserModel.role == role).all()

    def get_gerentes_by_coo(self, coo_id: int) -> list[UserModel]:
        times = self.db.query(TimeModel).filter(TimeModel.coo_id == coo_id).all()
        gerente_ids = {t.gerente_id for t in times if t.gerente_id is not None}
        resultado = self.db.query(UserModel).filter(UserModel.id.in_(gerente_ids)).all()
        self.db.close()
        return resultado

    def get_times_ids_by_gerente(self, gerente_id: int) -> list[int]:
        times = self.db.query(TimeModel).filter(TimeModel.gerente_id == gerente_id).all()
        resultado = [t.id for t in times]
        self.db.close()
        return resultado

    def get_colaboradores_by_gerente(self, gerente_id: int) -> list[UserModel]:
        times = self.db.query(TimeModel).filter(TimeModel.gerente_id == gerente_id).all()
        time_ids = [t.id for t in times]
        resultado = self.db.query(UserModel).filter(UserModel.time_id.in_(time_ids)).all()
        self.db.close()
        return resultado

    def search_colaboradores(self, query: str | None = None, time_ids: list[int] | None = None) -> list[UserModel]:
        base = self.db.query(UserModel).filter(UserModel.role == "colaborador")

        if time_ids is not None:
            base = base.filter(or_(UserModel.time_id.is_(None), UserModel.time_id.in_(time_ids)))

        if query:
            termo = f"%{query.strip()}%"
            base = base.filter(
                or_(
                    UserModel.full_name.ilike(termo),
                    UserModel.cpf.ilike(termo),
                )
            )

        return base.order_by(UserModel.full_name).limit(50).all()