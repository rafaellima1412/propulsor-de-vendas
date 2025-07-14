from src.infra.database.base import Base
from src.infra.database.session import engine

# ⬇️ Importa todos os modelos e tabelas de associação explicitamente

from src.infra.database.models.user_model import UserModel
from src.infra.database.models.campaign_model import CampanhaModel
from src.infra.database.models.venda_model import VendaModel
from src.infra.database.models.user_campaign import user_campanha
from src.infra.database.models.time_model import TimeModel

def init_db():
    # print("Tabelas conhecidas:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
