#!/bin/sh
get_cpu_limit()
{
    cfs_quota_us=$(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us)
    cfs_period_us=$(cat /sys/fs/cgroup/cpu/cpu.cfs_period_us)
    cpu_limit=$(expr ${cfs_quota_us} / ${cfs_period_us})
    if [[ ${cpu_limit} -ne 0 ]];then
        export CPU_LIMIT=${cpu_limit}
    else
        export CPU_LIMIT=0
    fi
}

export HOST=${flyer_host:-0.0.0.0}
export PORT=${flyer_port:-8080}
export BIND=${HOST}:${PORT}

# 通过容器CPU限制计算worker数，可以被flyer_workers变量覆盖
get_cpu_limit

if [[ ! -z ${flyer_workers} ]];then
    export WORKERS=${flyer_workers:-1}
elif [[ ${CPU_LIMIT} -ne 0 ]];then
    export WORKERS=$(expr \( ${CPU_LIMIT} \* 2 \) + 1)
else
    export WORKERS=1
fi

export THREADS=$(expr \( ${CPU_LIMIT} \* 4 \) + 1)
export max_requests=$(expr \( ${THREADS} \* 200 \) )
export max_requests=${flyer_max_requests:-${max_requests}}
export max_requests_jitter=${flyer_max_requests_jitter:-${max_requests}}

export GRACEFUL_TIMEOUT=${flyer_graceful_timeout:-10}
export TIMEOUT=${flyer_timeout:-10}
export THREADS=${flyer_threads:-${THREADS}}
export KEEPALIVE=${flyer_keepalive:-5}
export LOG_LEVEL=${flyer_log_level:-info}

if [[ "${flyer_reload}" == "True" ]];then
    export RELOAD="--reload"
fi

if [[ "${flyer_preload}" == "True" ]];then
    export PRELOAD="--preload"
fi

if [[ "${flyer_enable_max_requests}" == "True" ]];then
    export MAX_REQUESTS="--max-requests ${max_requests}"
    export MAX_REQUESTS_JITTER="--max-requests-jitter ${max_requests_jitter}"
fi
