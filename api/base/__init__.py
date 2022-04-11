from fastapi import APIRouter
from api.base import router

api_base = APIRouter()
api_base.include_router(router.router, tags=["健康检查"])
