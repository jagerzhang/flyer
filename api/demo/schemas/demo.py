# -*- coding: utf-8 -*-
"""
参数验证模块
"""
from typing import Optional, Union
from pydantic import BaseModel, Field
from api.settings import ierror


class DemoRequest(BaseModel):
    """ Demo演示：请求参数.
    """
    msgContent: str = Field(example="Flyer", title="Flyer演示项目")


class BaseResponse(BaseModel):
    """ Demo演示：响应参数.
    """
    msg: str = Field(default="Hello Flyer!",
                     example="Hello Flyer!",
                     title="Flyer演示项目返回信息")
    code: int = Field(
        default=ierror.IS_SUCCESS,
        example=ierror.IS_SUCCESS,  # NOQA
        title="Flyer演示项目返回码")


class PageInfo(BaseModel):
    """
    数据接口通用响应

    Args:
        BaseResponse (_type_): _description_
    """
    total: int = Field(
        default=0,
        example=0,  # NOQA
        title="返回数据总条数")
    offset: int = Field(
        default=1,
        example=1,  # NOQA
        title="返回数据的分页位置，用于按批次连续拉取")
    size: int = Field(
        default=50,
        example=50,  # NOQA
        title="返回数据的分页大小，默认为50")


class DataResponse(BaseResponse):
    """
    数据接口通用响应

    Args:
        BaseResponse (_type_): _description_
    """
    pagination: Optional[PageInfo] = Field(default={}, title="返回数据的页面信息")
    data: Union[list, dict] = Field(default=[], example=[], title="接口返回的详细数据")
