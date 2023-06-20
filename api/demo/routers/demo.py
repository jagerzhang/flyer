from fastapi import APIRouter, Request
from api.demo.schemas.demo import DemoRequest, DataResponse
from utils.middleware import RouteMiddleWare
from api.settings import ierror

router = APIRouter(route_class=RouteMiddleWare)


@router.post("/demo", response_model=DataResponse, summary="Demo")
async def demo(params: DemoRequest, request: Request):
    """
    Demo 演示接口
    ---
    - 功能说明: 用于演示 Flyer 开发框架，传入一个名字，返回 "Hello <名字>!"
    - 附加说明1: 详细的参数说明可以查看<a href="/flyer/v1/redoc#tag/Demo" \
target="_blank">接口文档</a>；
    - 附加说明2: 这个位置可以加入更多说明列表。
    """
    result = {"code": ierror.IS_SUCCESS, "msg": f"Hello {params.msgContent}!"}
    return result
