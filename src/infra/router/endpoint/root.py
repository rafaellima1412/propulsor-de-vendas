from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def health_check():
    """Health-check simples. A tela de login/landing agora é responsabilidade do frontend."""
    return {"status": "ok", "service": "Propulsor de vendas API"}
