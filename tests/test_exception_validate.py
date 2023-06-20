# -*- coding: utf-8 -*-
"""
测试 参数验证错误
"""
import os
import sys
abs_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(abs_path)
from api import create_app
from api.settings import prefix, ierror
from fastapi.testclient import TestClient

app = create_app()
client = TestClient(app)


def test():
    response = client.post(prefix + "/demo", json={})
    print(response.json())
    assert response.status_code == 200
    assert response.json().get(
        "code") == ierror.VALIDATE_REQUEST_PARAMS_ERROR


if __name__ == '__main__':
    test()
