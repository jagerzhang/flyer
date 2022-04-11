#!/bin/sh
test -f env_ext.sh && \
    source env_ext.sh

test -f docker/prestart.sh && \
    source docker/prestart.sh

exec gunicorn main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${WORKERS} \
    --bind ${BIND} \
    --graceful-timeout ${GRACEFUL_TIMEOUT} \
    --timeout ${TIMEOUT} \
    --threads ${THREADS}  ${MAX_REQUESTS} ${MAX_REQUESTS_JITTER} \
    --keep-alive ${KEEPALIVE} ${RELOAD} ${PRELOAD} \
    --log-level=${LOG_LEVEL}
