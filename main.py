# -*- coding: utf-8 -*-
from api import create_app
from api.settings import env

app = create_app()

if __name__ == "__main__":
    import uvicorn
    bind_host = env.get("flyer_host", "0.0.0.0")
    bind_port = env.get("flyer_port", 8080)
    is_reload = int(env.get("flyer_reload", 1))
    workers = int(env.get("flyer_workers", 1))
    log_level = env.get("flyer_log_level", "info")
    access_log = int(env.get("flyer_access_log", 1))
    uvicorn.run(app="main:app",
                host=bind_host,
                port=int(bind_port),
                log_level=log_level,
                access_log=access_log,
                reload=is_reload,
                workers=workers)
