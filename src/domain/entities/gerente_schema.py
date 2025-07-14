# from typing import List
#
# from pydantic import BaseModel
#
# from src.domain.entities.coo_schema import COOOut
#
#
# class GerenteBase(BaseModel):
#     nome: str
#     coo_id: int
#
# class GerenteCreate(GerenteBase):
#     pass
#
# class GerenteOut(GerenteBase):
#     times_ids: List[int] = []
#     colaboradores_ids: List[int] = []  # via time
