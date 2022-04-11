# -*- coding: utf-8 -*-
"""
测试 Health、文档等基础接口
"""
import sys
sys.path.append("..")
from api import create_app
from api.settings import base_url, version
from fastapi.testclient import TestClient

app = create_app()
client = TestClient(app)


def test():
    response = client.get(f"{base_url}/{version}/docs")
    assert response.status_code == 200

    response = client.get(f"{base_url}/{version}/redoc")
    assert response.status_code == 200


if __name__ == '__main__':
    test()
