# -*- coding: utf-8 -*-
"""
参数验证模块
"""
from pydantic import BaseModel, Field
from api.settings import ierror


class DemoRequest(BaseModel):
    """ Demo演示：请求参数.
    """
    msgContent: str = Field(example="Flyer", title="Flyer演示项目")


class DemoResponse(BaseModel):
    """ Demo演示：响应参数.
    """
    retInfo: str = Field(default="Hello Flyer!",
                         example="Hello Flyer!",
                         title="Flyer演示项目返回信息")
    retCode: int = Field(
        default=ierror.IS_SUCCESS,
        example=ierror.IS_SUCCESS,  # NOQA
        title="Flyer演示项目返回码")
