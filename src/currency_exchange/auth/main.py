from fastapi import APIRouter

from .routes import clients_router, token_router
from .admin import admin_router


auth_router = APIRouter()
auth_router.include_router(clients_router, prefix="/clients", tags=["auth"])
auth_router.include_router(token_router, prefix="/tokens", tags=["auth"])
