# -*- coding: utf-8 -*-
"""
测试Demo接口
"""
import os
import sys

abs_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(abs_path)
from api import create_app
from api.settings import prefix
from fastapi.testclient import TestClient

app = create_app()
client = TestClient(app)


def test():
    response = client.post(prefix + "/demo", json={"msgContent": "Flyer"})
    print(response.json())
    assert response.status_code == 200
    assert response.json().get("code") == 200
    assert response.json().get("msg") == "Hello Flyer!"


if __name__ == '__main__':
    test()
