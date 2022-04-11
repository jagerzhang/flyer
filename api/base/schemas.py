# -*- coding: utf-8 -*-
"""
验证参数
"""
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """ 健康检查响应参数.
    """
    retInfo: str = Field(example="success", title="接口返回信息")
    retCode: int = Field(example=200, title="请求返回码")
