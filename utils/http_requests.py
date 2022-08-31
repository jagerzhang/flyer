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
            exception, HTTPError) or isinstance(exception, NewConnectionError):
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
    if result.status_code in [400, 403, 404, 405, 426, 500, 502, 503, 504]:
        return True
    # 对于内容的判断需要根据业务场景自行发挥，代码略...
    return False


def requests(method, *args, **kwargs):
    """
    支持失败重试和记录日志的requests函数
    """
    @retry(
        stop_max_attempt_number=3,  # 失败最多重试3次
        stop_max_delay=10000,  # 函数运行总时长为10S
        retry_on_result=retry_by_result,  # 回调函数检查
        retry_on_exception=retry_by_except)  # 回调异常检查
    def _requests(method, *args, **kwargs):
        """
        支持失败重试和记录日志的requests函数
        """
        http_session = session()
        request_start = time.perf_counter()
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
        req_log["outBody"] = out_body
        req_log["outUrl"] = url
        req_log["outMethod"] = method
        if headers != {}:
            req_log["outHeaders"] = str(headers)

        resp = None
        resp = getattr(http_session, str(method).lower())(*args, **kwargs)
        req_log["outRetCode"] = resp.status_code
        # 图片类型忽略内容记录
        content_type = resp.headers.get("Content-Type", "")
        if content_type.startswith("image") or content_type == "":
            req_log[
                "outRetInfo"] = f"Content-Type: {content_type} no need record."

        else:
            req_log["outRetInfo"] = resp.text

        request_end = time.perf_counter()
        request_lasting = int((request_end - request_start) * 1000)
        req_log["latency"] = request_lasting

        config.logger.info(req_log)

        http_session.close()
        resp.close()

        return resp

    try:
        resp = _requests(method, *args, **kwargs)

    except RetryError:
        ret_info = "请求第三方服务异常, 经过多次重复仍然无法成功，请稍后再试"
        resp = Response(ret_info, config.ierror.VALIDATE_RESPONSE_CODE_ERROR)

    except Exception as err:  # pylint: disable=broad-except
        ret_info = f"请求第三方服务异常, 错误信息：{err}"
        resp = Response(ret_info, config.ierror.VALIDATE_RESPONSE_CODE_ERROR)

    finally:
        return resp
