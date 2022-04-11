# -*- coding: utf-8 -*-
from api import create_app
from api.settings import env_list

app = create_app()

if __name__ == "__main__":
    import uvicorn
    bind_host = env_list.get("flyer_host", "0.0.0.0")
    bind_port = env_list.get("flyer_port", 8080)
    is_reload = eval(env_list.get("flyer_reload", "True"))
    workers = int(env_list.get("flyer_workers", 1))
    log_level = env_list.get("flyer_log_level", "info")
    access_log = eval(env_list.get("flyer_access_log", "True"))
    uvicorn.run(app="main:app",
                host=bind_host,
                port=int(bind_port),
                log_level=log_level,
                access_log=access_log,
                reload=is_reload,
                workers=workers)
