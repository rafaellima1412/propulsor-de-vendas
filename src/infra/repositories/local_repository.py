import re

from geoalchemy2.elements import WKTElement
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.application.repositories.ilocal_repository import ILocalRepository
from src.domain.entities.local_schema import Coordenadas, LocalCreate, LocalSchema, LocalUpdate
from src.infra.database.models.local_model import Local

# "shapely" (usado por geoalchemy2.shape.to_shape) não é dependência do
# projeto, então lemos o ponto de volta como texto WKT ("POINT(lon lat)")
# via ST_AsText, sem precisar de bibliotecas geoespaciais extras.
_POINT_RE = re.compile(r"POINT\(([-\d.]+)\s+([-\d.]+)\)")


def _make_point(coordenadas: Coordenadas) -> WKTElement:
    return WKTElement(f"POINT({coordenadas.longitude} {coordenadas.latitude})", srid=4326)


def _to_schema(local: Local, wkt: str | None) -> LocalSchema:
    latitude, longitude = 0.0, 0.0
    if wkt:
        match = _POINT_RE.match(wkt)
        if match:
            longitude, latitude = float(match.group(1)), float(match.group(2))

    return LocalSchema(
        id=local.id,
        nome=local.nome,
        coordenadas=Coordenadas(latitude=latitude, longitude=longitude),
    )


class LocalRepository(ILocalRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[LocalSchema]:
        rows = self.db.query(Local, func.ST_AsText(Local.coordenadas)).all()
        self.db.close()
        return [_to_schema(local, wkt) for local, wkt in rows]

    def get_by_id(self, local_id: int) -> LocalSchema | None:
        row = (
            self.db.query(Local, func.ST_AsText(Local.coordenadas))
            .filter(Local.id == local_id)
            .first()
        )
        self.db.close()
        if not row:
            return None

        local, wkt = row
        return _to_schema(local, wkt)

    def create(self, data: LocalCreate) -> LocalSchema:
        novo_local = Local(nome=data.nome, coordenadas=_make_point(data.coordenadas))
        self.db.add(novo_local)
        self.db.commit()
        self.db.refresh(novo_local)

        local_id = novo_local.id
        self.db.close()

        return LocalSchema(id=local_id, nome=data.nome, coordenadas=data.coordenadas)

    def update(self, local_id: int, data: LocalUpdate) -> LocalSchema | None:
        local = self.db.query(Local).filter(Local.id == local_id).first()
        if not local:
            self.db.close()
            return None

        if data.nome is not None:
            local.nome = data.nome
        if data.coordenadas is not None:
            local.coordenadas = _make_point(data.coordenadas)

        self.db.commit()
        self.db.refresh(local)

        wkt = self.db.query(func.ST_AsText(Local.coordenadas)).filter(Local.id == local_id).scalar()
        updated = _to_schema(local, wkt)

        self.db.close()
        return updated

    def delete(self, local_id: int) -> None:
        local = self.db.query(Local).filter(Local.id == local_id).first()
        if local:
            self.db.delete(local)
            self.db.commit()
        self.db.close()
