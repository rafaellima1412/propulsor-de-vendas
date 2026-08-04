import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from config.settings import BASE_DIR
from src.infra.database.init_db import init_db
from src.infra.dy.container import Container
from src.infra.router.routers import routers as v1_routers
from src.infra.settings.settings import settings

container = Container()

container.wire(
    modules=[
        "src.application.auth.auth",
        "src.infra.router.endpoint.user_route",
        "src.infra.router.endpoint.venda_route",
        "src.infra.router.endpoint.carteira_route",
        "src.infra.router.endpoint.campaign_route",
        "src.infra.router.endpoint.team_route",
        "src.infra.router.endpoint.local_route",
    ]
)


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()

    application.container = container

    yield

    container.unwire()


app = FastAPI(
    lifespan=lifespan,
    title="Propulsor de vendas API",
    description="API de gestão de campanhas, vendas e carteira financeira.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_routers)


app.mount(
    "/media",
    StaticFiles(directory=os.path.join(BASE_DIR, "media")),
    name="media",
)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    return JSONResponse(
        content={"detail": exc.detail},
        status_code=exc.status_code,
    )