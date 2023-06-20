#!/bin/bash
export flyer_host=${flyer_host:-0.0.0.0}
export flyer_port=${flyer_port:-8083}
export flyer_reload=${flyer_reload:-1}
export flyer_workers=${flyer_workers:-1}
export flyer_report_log=${flyer_report_log:-0}
export flyer_log_level=${flyer_log_level:-debug}
export flyer_access_log=${flyer_access_log:-1}

test -f env_ext.sh && \
    source env_ext.sh

exec python3 main.py
