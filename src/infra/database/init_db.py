from src.infra.database.base import Base
from src.infra.database.models.campaign_model import CampanhaModel  # noqa: F401
from src.infra.database.models.local_model import Local  # noqa: F401
from src.infra.database.models.user_campaign import user_campanha  # noqa: F401

# ⬇️ Importa todos os modelos e tabelas de associação explicitamente
from src.infra.database.models.venda_model import VendaModel  # noqa: F401
from src.infra.database.session import engine


def init_db():
    # print("Tabelas conhecidas:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
