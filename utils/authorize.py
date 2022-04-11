import secrets
from fastapi import Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from api import settings as config

security = HTTPBasic()


def authorize(credentials: HTTPBasicCredentials = Depends(security)):
    """支持SwaggerUI开启BasicAuth鉴权

    使用说明：
        1. 需要在配置中配置BasicAuth帐号和密码，分别用 flyer_auth_user 和 flyer_auth_pass 变量；
        2. 修改 api.__init__.py 如下修改：
            a. 新加载模块：
                from fastapi import Depends
                from utils.authorize import authorize
            
            b. 继续在这个文件中找到如下类似路由加载配置：
                app.include_router(demo_api, prefix=f"{config.base_url}/{config.version}")

            改为：
                if int(config.env_list.get("flyer_auth_enable", 0)) == 1:
                    app.include_router(demo_api,
                                    prefix=f"{config.base_url}/{config.version}",
                                    dependencies=[Depends(authorize)])
                else:
                    app.include_router(demo_api,
                                prefix=f"{config.base_url}/{config.version}")
                            
            即：当环境变量 flyer_auth_enable 设置为1的时候，此路由将开启BasicAuth鉴权

    """
    is_user_ok = secrets.compare_digest(credentials.username,
                                        config.env_list.get("flyer_auth_user"))
    is_pass_ok = secrets.compare_digest(credentials.password,
                                        config.env_list.get("flyer_auth_pass"))
    if not (is_user_ok and is_pass_ok):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect user or password.",
                            headers={"WWW-Authenticate": "Basic"})
