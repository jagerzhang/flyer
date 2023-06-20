import re
import time
import json
from urllib3.exceptions import HTTPError
from urllib3.exceptions import ResponseError
from urllib3.exceptions import NewConnectionError
from requests import session
from retrying import retry, RetryError
from api import settings as config


class Response():
    """模拟requests返回，实现返回类型统一
    """

    def __init__(self, text, status_code, resp=None) -> None:
        self.text = text
        self.status_code = status_code
        self.resp = resp
        self.headers = {}


def retry_by_except(exception):
    """根据Exception类型发起重试
    """
    if isinstance(exception, ResponseError) or isinstance(
            exception, HTTPError) or isinstance(
                exception, NewConnectionError) or isinstance(
                    exception, ConnectionResetError):
        config.logger.warning(
            f"request failed, exception info: {str(exception)}, retrying...")
        return True

    # 其他异常不重试，仅上报一条告警
    config.alarm.report_string(str(exception))
    return False


def retry_by_result(result):
    """根据返回结果发起重试
    """
    # 异常状态码进行重试
    if result.status_code in [
            400, 403, 404, 405, 426, 429, 500, 502, 503, 504
    ]:
        return True
    # 对于内容的判断需要根据业务场景自行发挥，代码略...
    return False


class Requests():
    """
    支持失败重试和记录日志的requests函数
    """

    def __init__(self, report_log: bool = True, **kwargs):
        """
        初始化

        Args:
            report_log (bool, optional): 是否上报日志. Defaults to True.
            kwargs (dict)：retrying重试设置，参数请查看：https://github.com/groodt/retrying
        """
        self.report_log = report_log

        # 默认重试3次，10S重试超时
        self.kwargs = {"stop_max_attempt_number": 3, "stop_max_delay": 10000}

        # 自动植入retrying参数，传入错误参数将会报错。
        for k, v in kwargs.items():
            self.kwargs[re.sub(r"[A-Z]",
                               lambda match: f"_{match.group(0).lower()}",
                               k)] = v

    def requests(self, method: str, *args, **kwargs):
        """
        Requests HTTP请求

        Args:
            method (str): HTTP请求方法，不区分大小写

        Raises:
            HTTPError: 请求异常

        Returns:
            Response: Requests的响应对象
        """

        @retry(retry_on_result=retry_by_result,
               retry_on_exception=retry_by_except,
               **self.kwargs)
        def _requests(method, *args, **kwargs):
            """
            HTTP请求
            """
            request_start = time.perf_counter()
            http_session = session()
            url = kwargs.get("url", "")
            headers = kwargs.get("headers", {})
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
            resp = getattr(http_session, str(method).lower())(*args, **kwargs)
            req_log["out_code"] = resp.status_code
            # 图片类型忽略内容记录
            content_type = resp.headers.get("Content-Type", "")
            if content_type.startswith("image") or content_type == "":
                req_log[
                    "out_msg"] = f"Content-Type: {content_type} no need record."

            else:
                req_log["out_code"] = resp.text

            request_end = time.perf_counter()
            req_log["out_latency"] = int((request_end - request_start) * 1000)

            if self.report_log:
                config.logger(req_log)

            http_session.close()
            resp.close()

            return resp

        try:
            resp = _requests(method, *args, **kwargs)

        except RetryError as err:
            ret_info = f"请求第三方服务异常, 经过多次重复仍然无法成功，错误信息：{err}"
            resp = Response(ret_info,
                            config.ierror.VALIDATE_RESPONSE_CONTENT_ERROR)

        except ConnectionResetError as err:
            raise HTTPError(f"网络连接错误: {err}")

        except Exception as err:  # pylint: disable=broad-except
            ret_info = f"请求第三方服务异常, 错误信息：{err}"
            config.logger.warning(f"Request Error: {ret_info}")
            resp = Response(ret_info,
                            config.ierror.VALIDATE_RESPONSE_CODE_ERROR)

        finally:
            return resp
