# -*- coding: utf-8 -*-
"""
测试 Health 接口
"""
import sys
sys.path.append("..")
from api import create_app
from fastapi.testclient import TestClient

app = create_app()
client = TestClient(app)


def test():
    response = client.get("/health_check")
    print(response.text)
    assert response.status_code == 200
    assert response.json().get("retCode") == 200


if __name__ == '__main__':
    test()
