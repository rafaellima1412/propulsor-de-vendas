from fastapi import APIRouter

from src.infra.router.endpoint.campaign_route import router as campaign_router
from src.infra.router.endpoint.carteira_route import router as carteira_router
from src.infra.router.endpoint.local_route import router as local_router
from src.infra.router.endpoint.root import router as root_router
from src.infra.router.endpoint.team_route import router as team_router
from src.infra.router.endpoint.user_route import router as user_router
from src.infra.router.endpoint.venda_route import router as venda_router

routers = APIRouter()

routers.include_router(campaign_router)
routers.include_router(carteira_router)
routers.include_router(user_router)
routers.include_router(venda_router)
routers.include_router(root_router)
routers.include_router(team_router)
routers.include_router(local_router)