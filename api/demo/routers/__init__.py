from fastapi import APIRouter
from api.demo.routers import demo

demo_api = APIRouter()
demo_api.include_router(demo.router, tags=["Demo接口"])
