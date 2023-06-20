import time
import json
from urllib3.exceptions import HTTPError
from urllib3.exceptions import ResponseError
from urllib3.exceptions import NewConnectionError
from httpx import AsyncClient
import tenacity
from aiohttp import ClientError, ClientConnectionError, ClientOSError, ClientConnectorError, ClientProxyConnectionError
from api import settings as config

session = AsyncClient()


class Response():
    """模拟requests返回，实现返回类型统一
    """

    def __init__(self, text, status_code, resp=None) -> None:
        self.text = text
        self.status_code = status_code
        self.resp = resp
        self.headers = {}


def should_retry(response):
    if response is None:
        return True
    if response is not None and response.status_code in [500, 504, 503, 502]:
        return True
    return False


class Requests():

    def __init__(self, **kwargs):
        """
        重试参数：
        tenacity 库提供了非常丰富的重试（retry）配置选项，下面将列出 retry 装饰器中所有可选参数并进行简要说明：
            stop: 定义应何时停止重试的策略。可以使用内置的 stop_* 函数，也可以使用自定义的 callable 对象。例如，使用
            stop_after_attempt(3) 可以定义最多尝试 3 次请求后停止重试。默认情况下，stop 选项设置为 stop_never，表示无限重试。

            wait: 定义重试之间的等待时间。可以使用内置的 wait_* 函数，也可以使用自定义的 callable 对象。

            before: 可选的回调函数，在每次进行重试之前执行。回调函数的参数是 RetryCallState 对象。

            after: 可选的回调函数，在每次重试之后执行。回调函数的参数是 RetryCallState 对象。

            retry: 可选的回调函数，在每次重试之前执行。如果返回的结果是 False，则终止重试。
            回调函数的参数是 RetryCallState 对
            象。

            before_sleep: 在等待重试次数之前执行的可选回调函数。在等待发生之前，每次迭代周期都会执行此回调。
            回调函数的参数是 RetryCallState 对象。可以使用它来加入自定义日志记录、指令或测试传递信息。

            after_retry: 可选的回调函数，在每次重试时执行。回调函数的参数是 RetryCallState 对象。

            retry_error_callback: 可选的回调函数，在重试策略发生故障时执行（例如，无法在规定时间内停止)，
            回调函数的参数是 RetryCallState 对象。

            reraise: 如果在 retry 过程中遇到了未处理的异常，则该选项指定是否 reraise 异常。默认值为 True，即立即 reraise。

            before_retry: “只要在 retry 发生时，无论是通过异常还是通过指数退避，都将在 retry 前调用”。
            将在 retry=retry 的类型中添加此回调。

            retry_error_cls: 指定应当被 classified（分类）字符串的想弄死。当在 retry 中间产生一个重试错误时，
            应当将它识别为这些字符串之一。
        """
        self.retry_config = {
            "wait":
            tenacity.wait_fixed(1),
            "stop":
            tenacity.stop_any(
                (tenacity.stop_after_delay(10)),
                tenacity.stop_after_attempt(3),
            ),
            "retry":
            tenacity.retry_any(
                tenacity.retry_if_result(should_retry),
                tenacity.retry_if_exception_type(
                    (ClientError, ClientConnectionError, ClientOSError,
                     ClientConnectorError, ClientProxyConnectionError,
                     HTTPError, ResponseError, NewConnectionError)),
            )
        }

        self.retry_config.update(kwargs)

    async def requests(self, method, *args, **kwargs):
        """
        支持失败重试和记录日志的requests函数
        """

        @tenacity.retry(**self.retry_config)
        async def _requests(method, *args, **kwargs):
            """
            支持失败重试和记录日志的requests函数
            """
            request_start = time.perf_counter()
            url = kwargs.get("url", "")
            headers = kwargs.get("headers", {})
            headers["user-agent"] = "Flyer/v1.0.0"
            body = kwargs.get("json")
            if "timeout" not in kwargs:
                kwargs["timeout"] = 8

            if body is None:
                body = kwargs.get("params")

            if body is None:
                body = kwargs.get("data", "")

            if isinstance(body, dict):
                out_body = json.dumps(body)

            else:
                try:
                    out_body = str(body.to_string)

                except AttributeError:
                    out_body = str(body)

                except Exception as error:  # pylint: disable=broad-except
                    config.logger.warning(error)
                    out_body = str(error)

            req_log = {}
            req_log["out_body"] = out_body
            req_log["out_url"] = url
            req_log["out_method"] = method
            if headers != {}:
                req_log["out_headers"] = str(headers)

            resp = None
            resp = await getattr(session, str(method).lower())(*args, **kwargs)
            resp.raise_for_status()
            req_log["out_code"] = resp.status_code
            # 图片类型忽略内容记录
            content_type = resp.headers.get("Content-Type", "")
            if content_type.startswith("image") or content_type == "":
                req_log[
                    "out_msg"] = f"Content-Type: {content_type} no need record."

            else:
                req_log["out_msg"] = resp.text

            request_end = time.perf_counter()
            request_lasting = int((request_end - request_start) * 1000)
            req_log["out_latency"] = request_lasting

            config.logger.info(f"Out Request: {req_log}")

            return resp

        resp = await _requests(method, *args, **kwargs)
        try:
            resp = await _requests(method, *args, **kwargs)

        except Exception as err:  # pylint: disable=broad-except
            ret_info = f"请求第三方服务异常, 错误信息：{err}"
            config.logger.warning(f"Request Error: {ret_info}")
            resp = Response(ret_info, 40002)

        finally:
            return resp
