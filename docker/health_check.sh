#!/bin/bash
cd $(cd $(dirname $0) && pwd)

if [[ $(curl -sSL -o /dev/null -w "%{http_code}" http://127.0.0.1:${flyer_port:-8080}/health_check) -ne 200 ]];then
    exit 1
fi

# 自动重载释放释放内存
max_memory_usage_rate=${flyer_max_mem_usage_rate:-0.8}

auto_reload() {
    total_mem_usage=$(awk '/total_rss / {print $2}' /sys/fs/cgroup/memory/memory.stat)
    total_mem_limit=$(cat /sys/fs/cgroup/memory/memory.limit_in_bytes)
    mem_usage_rate=$(awk 'BEGIN{printf "%.2f\n",('$total_mem_usage'/'$total_mem_limit')}')
    if [[ $(expr ${mem_usage_rate} \> ${max_memory_usage_rate}) -eq 1 ]];then
        kill -HUP 1
    fi
}

# 是否开启自动释放内存机制
if [[ ${flyer_auto_reload} -eq 1 ]];then
    auto_reload
fi
