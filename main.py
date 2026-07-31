import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config.settings import BASE_DIR
from src.infra.database.init_db import init_db
from src.infra.dy.container import Container
from src.infra.router.routers import routers as v1_routers


container = Container()

container.wire(
    modules=[
        "src.application.auth.auth",
        "src.infra.router.endpoint.user_route",
        "src.infra.router.endpoint.venda_route",
        "src.infra.router.endpoint.campaign_route",
        "src.infra.router.endpoint.team_route",
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

app.include_router(v1_routers)


templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    if exc.status_code == 403:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": exc.detail,
            },
            status_code=403,
        )

    if exc.status_code == 404:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": "Página não encontrada",
            },
            status_code=404,
        )

    return HTMLResponse(
        content=str(exc.detail),
        status_code=exc.status_code,
    )