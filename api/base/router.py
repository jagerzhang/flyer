from api.base.schemas import HealthCheckResponse
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from api import settings as config

router = APIRouter()


@router.get(f"{config.prefix}/health_check", include_in_schema=True)
async def health_check():  # NOQA
    """健康检查接口
    """
    return JSONResponse(content={
        "retInfo": "success",
        "retCode": config.ierror.IS_SUCCESS
    })


@router.get(f"{config.base_url}/{config.version}/docs",
            include_in_schema=False)
async def docs():  # NOQA
    """ Swagger UI
    """
    return get_swagger_ui_html(
        openapi_url=config.prefix + "/openapi.json",
        title=config.API_TITLE + "接口交互文档",
        swagger_js_url=config.base_url + "/static/swagger-ui-bundle.js",
        swagger_css_url=config.base_url + "/static/swagger-ui.css",
        swagger_favicon_url=config.base_url + "/static/favicon.ico")


@router.get(f"{config.base_url}/{config.version}/redoc",
            include_in_schema=False)
async def redoc():
    """ ReDoc UI
    """
    return get_redoc_html(
        openapi_url=config.prefix + "/openapi.json",
        title=config.API_TITLE + "接口交互文档",
        redoc_js_url=config.base_url + "/static/redoc.standalone.js",
        redoc_favicon_url=config.base_url + "/static/favicon.ico",
        with_google_fonts=False)
