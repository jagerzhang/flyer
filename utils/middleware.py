# -*- coding: utf-8 -*-
import json
import time
import uuid
import resource
import traceback
from fastapi.routing import APIRoute
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import ValidationError, RequestValidationError
from starlette.exceptions import HTTPException
from api import settings as config


class RouteMiddleWare(APIRoute):
    """路由中间件：记录请求日志和耗时等公共处理逻辑
    """
    async def get_request_body(self, request):
        """获取请求参数
        """
        request_body = await request.body()
        try:
            request_body = json.loads(request_body)

        except Exception:  # pylint: disable=broad-except
            try:
                request_body_str = bytes.decode(request_body)

            except UnicodeDecodeError:
                request_body_str = str(request_body)

            request_body = {"request_str": request_body_str}

        return request_body

    async def report_log(self, request_body, response, **kwargs):
        """记录自定义请求日志
        """
        # 尝试序列化响应内容
        try:
            response_body = json.loads(response.body)

        except Exception:  # pylint: disable=broad-except
            try:
                response_body = {"response_str": bytes.decode(response.body)}
            except UnicodeDecodeError:
                response_body = {"response_str": ""}

        if isinstance(response_body, dict) and isinstance(request_body, dict):
            response_body.update(request_body)

            if "retCode" not in response_body:
                response_body["retCode"] = response.status_code

            if "retInfo" not in response_body:
                response_body["retInfo"] = str(
                    response_body.get("response_str"))

        response_body.update(kwargs)

        if eval(config.env_list.get("flyer_access_log_json", "True")):
            config.logger.info(json.dumps(response_body))

    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def recorder(request: Request) -> Response:
            start_time = time.perf_counter()
            # 计算线程内存占用
            memory_usage_begin = resource.getrusage(
                resource.RUSAGE_THREAD).ru_maxrss
            # 对接NGate网关记录客户端ID
            client_id = request.headers.get("x-client-id", "")
            request_id = request.headers.get("x-request-id")
            if not request_id:
                request_id = str(uuid.uuid4())

            client_ip = config.common_func.get_client_ip(request)

            # FastAPI 0.68.2 开始必须要传入 application/json 才识别为字典，否则报错，这里先兼容下，需要推动客户端整改后去掉
            # https://github.com/tiangolo/fastapi/releases/tag/0.65.2
            request.headers.__dict__["_list"].insert(
                0, (b"content-type", b"application/json"))

            # 尝试序列化请求参数
            request_body = await self.get_request_body(request)

            result = None
            try:

                response: Response = await original_route_handler(request)
                result = None

            # 鉴权失败
            except HTTPException as error:
                result = None
                raise error

            # 捕获参数异常
            except RequestValidationError as error:
                ret_info = f"请求参数错误，请检查您的请求字段属性是否正确，如有疑问请联系管理员，报错信息: {error}"
                error_str = f"请求参数错误，X-Request-ID: {request_id}，报错信息: {error}"
                result = {
                    "retCode": config.ierror.VALIDATE_REQUEST_PARAMS_ERROR,
                    "clientIp": client_ip,
                    "retInfo": ret_info,
                    "logId": request_id
                }

            # 捕获响应异常
            except ValidationError as error:
                ret_info = f"响应参数错误，可能是依赖的服务返回异常，请稍后重试或联系管理员，报错信息: {error}"
                error_str = f"响应参数错误，X-Request-ID: {request_id}，报错信息: {error}"
                result = {
                    "retCode": config.ierror.VALIDATE_RESPONSE_CONTENT_ERROR,
                    "clientIp": client_ip,
                    "retInfo": ret_info,
                    "logId": request_id
                }

            # 捕获其他异常
            except Exception as error:  # pylint: disable=broad-except
                if "timed out" in traceback.format_exc():
                    ret_code = config.ierror.VALIDATE_RESPONSE_CODE_ERROR
                    ret_info = f"请求第三方接口出现超时，请稍后重试或联系管理员并提供logId。"
                    error_str = f"请求第三方接口出现超时，X-Request-ID: {request_id}，报错信息: {traceback.format_exc()}"

                else:
                    ret_code = config.ierror.INNER_SELF_ERROR
                    ret_info = f"发生内部错误，请联系管理员并提供logId。"
                    error_str = f"发生内部错误，X-Request-ID: {request_id}，报错信息: {traceback.format_exc()}"

                result = {
                    "retCode": ret_code,
                    "clientIp": client_ip,
                    "retInfo": ret_info,
                    "logId": request_id
                }

            # 如果有异常则执行返回
            finally:
                if result:
                    error = f"捕获到异常\nURL:{request.url}\nHeaders:{request.headers}\n\
X-Request-ID:{request_id}\nTraceInfo: {error_str}\nBody: {request_body}"

                    config.alarm.report_string(error)
                    response = JSONResponse(content=result)

            # 插入自定义头部
            memory_usage_end = resource.getrusage(
                resource.RUSAGE_THREAD).ru_maxrss

            memory_usage = memory_usage_end - memory_usage_begin
            total_lasting = int((time.perf_counter() - start_time) * 1000)
            response.headers["X-Lasting-Time"] = str(total_lasting)
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Memory-Usage"] = f"{memory_usage}KB"
            # 防御 XSS 反射型漏洞
            response.headers["X-Content-Type-Options"] = "nosniff"

            await self.report_log(
                request_body,
                response,
                timeStamp=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                latency=total_lasting,
                clientIp=client_ip,
                memoryUsage=memory_usage,
                logId=request_id,
                Url=str(request.url),
                clientId=str(client_id),
                xForwardedFor=request.headers.get("x-forwarded-for", ""),
                userAgent=request.headers.get("user-agent", ""))

            return response

        return recorder
