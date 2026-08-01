from enum import Enum


class PlanoInternet(str, Enum):
    MB_500 = "500MB"
    GB_1 = "1GB"
    GB_2 = "2GB"
    GB_10 = "10GB"


class StatusVenda(str, Enum):
    vendido = "vendido"
    pendente = "pendente"
    cancelado = "cancelado"
