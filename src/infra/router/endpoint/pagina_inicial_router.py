from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.application.auth.auth import get_current_user

router = APIRouter(prefix="/pagina", tags=["Initial"])
templates = Jinja2Templates(directory="templates")


@router.get("/inicial", response_class=HTMLResponse)
def initial_page(
    request: Request,
    user: dict = Depends(get_current_user),
):
    return templates.TemplateResponse(request, "pagina_inicial.html", {"user": user})
