# src/application/auth/permissions.py

from fastapi import Depends, HTTPException

from src.application.auth.auth import get_current_user


def require_role(*roles: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Acesso negado")
        return user

    return checker


# Roles individuais
require_admin = require_role("admin")
require_coordenador = require_role("coordenador")
require_gerente = require_role("gerente")

# Combinações reutilizadas em múltiplos routers
require_gerente_ou_coordenador = require_role("gerente", "coordenador")
require_coordenador_ou_admin = require_role("coordenador", "admin")