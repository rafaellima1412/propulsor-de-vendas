import re

from sqlalchemy import extract, func
from sqlalchemy.orm import Session, joinedload

from src.application.dtos.venda_create_dto import VendaCreateDTO
from src.domain.enums.enums import PlanoInternet
from src.infra.database.models.campaign_model import CampanhaModel
from src.infra.database.models.local_model import Local
from src.infra.database.models.venda_model import VendaModel

# mesmo padrão usado em local_repository.py pra ler o ponto de volta como
# texto (WKT) via ST_AsText, sem depender de "shapely".
_POINT_RE = re.compile(r"POINT\(([-\d.]+)\s+([-\d.]+)\)")


class VendaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, venda: VendaCreateDTO):
        db_venda = VendaModel(**venda.model_dump())
        self.db.add(db_venda)
        self.db.commit()
        self.db.refresh(db_venda)
        # Recarrega com os relacionamentos já prontos, pra devolver via
        # VendaOut sem precisar de uma query extra.
        resultado = (
            self.db.query(VendaModel)
            .options(joinedload(VendaModel.usuario), joinedload(VendaModel.campanha))
            .filter(VendaModel.id == db_venda.id)
            .first()
        )
        self.db.close()
        return resultado

    def get_all(self):
        resultado = (
            self.db.query(VendaModel)
            .options(joinedload(VendaModel.usuario), joinedload(VendaModel.campanha))
            .order_by(VendaModel.data_criacao.desc())
            .all()
        )
        self.db.close()
        return resultado

    def get_by_usuario_ids(self, usuario_ids: list[int]) -> list[VendaModel]:
        if not usuario_ids:
            self.db.close()
            return []
        resultado = (
            self.db.query(VendaModel)
            .options(joinedload(VendaModel.usuario), joinedload(VendaModel.campanha))
            .filter(VendaModel.usuario_id.in_(usuario_ids))
            .order_by(VendaModel.data_criacao.desc())
            .all()
        )
        self.db.close()
        return resultado

    def get_by_id(self, venda_id: int):
        resultado = self.db.query(VendaModel).filter(VendaModel.id == venda_id).first()
        self.db.close()
        return resultado

    def contagem_por_plano(self, usuario_ids: int | list[int]) -> dict[str, int]:
        if isinstance(usuario_ids, int):
            usuario_ids = [usuario_ids]

        if not usuario_ids:
            self.db.close()
            return {}
        # print(usuario_ids, type(usuario_ids))
        resultados = (
            self.db.query(VendaModel.plano, func.count(VendaModel.id))
            .filter(
                VendaModel.status == "vendido",
                VendaModel.usuario_id.in_(usuario_ids),
            )
            .group_by(VendaModel.plano)
            .all()
        )
        self.db.close()

        return {
            plano.value if isinstance(plano, PlanoInternet) else plano: count
            for plano, count in resultados
        }

    def contagem_por_mes(self,usuario_ids: int | list[int]) -> dict[tuple[int, int], int]:
        if isinstance(usuario_ids, int):
            usuario_ids = [usuario_ids]

        if not usuario_ids:
            self.db.close()
            return {}

        resultados = (
            self.db.query(
                extract("year", VendaModel.data_criacao).label("ano"),
                extract("month", VendaModel.data_criacao).label("mes"),
                func.count(VendaModel.id),
            )
            .filter(
                VendaModel.status == "vendido",
                VendaModel.usuario_id.in_(usuario_ids),
            )
            .group_by("ano", "mes")
            .order_by("ano", "mes")
            .all()
        )
        self.db.close()

        return {
            (int(ano), int(mes)): count
            for ano, mes, count in resultados
        }

    def ranking_por_usuario(self, usuario_ids: list[int]) -> dict[int, int]:
        """Quantas vendas com status 'vendido' cada usuário tem, entre os
        ids informados. Devolve só quem tem pelo menos 1 venda — quem não
        vendeu nada fica de fora (o chamador completa com 0 se quiser)."""
        if not usuario_ids:
            self.db.close()
            return {}

        resultados = (
            self.db.query(VendaModel.usuario_id, func.count(VendaModel.id))
            .filter(
                VendaModel.status == "vendido",
                VendaModel.usuario_id.in_(usuario_ids),
            )
            .group_by(VendaModel.usuario_id)
            .all()
        )
        self.db.close()

        return {usuario_id: count for usuario_id, count in resultados}

    def mapa_calor(self, coordenador_id: int | None = None) -> list[dict]:
        """Total de vendas ('vendido') por local de campanha — pra plotar
        num mapa de pontos quentes. Quando coordenador_id é informado,
        conta só as campanhas desse coordenador; senão, conta a empresa
        toda."""
        query = (
            self.db.query(
                Local.id,
                Local.nome,
                func.ST_AsText(Local.coordenadas),
                func.count(VendaModel.id),
            )
            .join(CampanhaModel, CampanhaModel.local_id == Local.id)
            .join(VendaModel, VendaModel.campanha_id == CampanhaModel.id)
            .filter(VendaModel.status == "vendido")
        )

        if coordenador_id is not None:
            query = query.filter(CampanhaModel.coordenador_id == coordenador_id)

        query = query.group_by(Local.id, Local.nome)
        linhas = query.all()
        self.db.close()

        resultados = []
        for local_id, nome, wkt, total in linhas:
            latitude, longitude = 0.0, 0.0
            if wkt:
                match = _POINT_RE.match(wkt)
                if match:
                    longitude, latitude = float(match.group(1)), float(match.group(2))
            resultados.append(
                {
                    "local_id": local_id,
                    "nome": nome,
                    "latitude": latitude,
                    "longitude": longitude,
                    "total_vendas": total,
                }
            )
        return resultados

    def contagem_por_plano_all(self) -> dict[str, int]:
        """Igual a contagem_por_plano, mas sem filtro de usuário — todas as vendas da empresa."""
        resultados = (
            self.db.query(VendaModel.plano, func.count(VendaModel.id))
            .filter(VendaModel.status == "vendido")
            .group_by(VendaModel.plano)
            .all()
        )
        self.db.close()

        return {
            plano.value if isinstance(plano, PlanoInternet) else plano: count
            for plano, count in resultados
        }

    def contagem_por_mes_all(self) -> dict[tuple[int, int], int]:
        """Igual a contagem_por_mes, mas sem filtro de usuário — todas as vendas da empresa."""
        resultados = (
            self.db.query(
                extract("year", VendaModel.data_criacao).label("ano"),
                extract("month", VendaModel.data_criacao).label("mes"),
                func.count(VendaModel.id),
            )
            .filter(VendaModel.status == "vendido")
            .group_by("ano", "mes")
            .order_by("ano", "mes")
            .all()
        )
        self.db.close()

        return {
            (int(ano), int(mes)): count
            for ano, mes, count in resultados
        }