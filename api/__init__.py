# -*- coding: utf-8 -*-
"""
APP加载入口
"""
import os
import uuid
import traceback
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from api import settings as config
from api.base import api_base
from utils.authorize import authorize
from api.demo.routers import demo_api

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app():
    """加载应用入口
    """
    app = FastAPI(title=config.API_TITLE,
                  description=config.DESCRIPTION,
                  version=config.version,
                  openapi_url=config.prefix + "/openapi.json",
                  docs_url=None,
                  redoc_url=None)
    app.mount(config.base_url + "/static",
              StaticFiles(directory=base_dir + "/static"),
              name="static")
    app.include_router(api_base)

    # 是否开启鉴权
    if int(config.env_list.get("flyer_auth_enable", 0)) == 1:
        app.include_router(demo_api,
                           prefix=f"{config.base_url}/{config.version}",
                           dependencies=[Depends(authorize)])
    else:
        app.include_router(demo_api,
                           prefix=f"{config.base_url}/{config.version}")

    create_service(app)
    register_exception(app)
    return app


def create_service(app: FastAPI):
    """
    把服务挂载到app对象上面
    :param app:
    :return:
    """
    @app.on_event("startup")
    def set_default_executor():  # pylint: disable=unused-variable
        max_threads = int(os.environ.get("THREADS", 5))
        config.logger.info(f"FastAPI Threads Number: {max_threads}")
        loop = asyncio._get_running_loop()
        loop.set_default_executor(ThreadPoolExecutor(max_workers=max_threads))


def register_exception(app: FastAPI):  # NOQA
    """
    全局异常捕获
    :param app:
    :return:
    """
    @app.exception_handler(Exception)
    def __all_exception_handler(request: Request, exc: Exception):  # noqa
        request_id = str(uuid.uuid4())
        error_str = f"全局异常\nURL:{request.url}\nHeaders:{request.headers}\n\
X-Request-ID:{request_id}\n{traceback.format_exc()}"

        client_ip = config.common_func.get_client_ip(request)
        result = {
            "retCode": config.ierror.INNER_SELF_ERROR,
            "retInfo": error_str,
            "clientIp": client_ip,
            "logId": request_id
        }
        result["retInfo"] = "服务出现异常，可能是您的请求协议JSON格式错误或者飞鸽依赖的服务返回异常，请稍后重试或\
联系管理员，报错信息: {}".format(traceback.format_exc(limit=0, chain=False))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=result,
        )
