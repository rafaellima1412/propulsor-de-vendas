from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request, APIRouter

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html", 
        {"user": None})