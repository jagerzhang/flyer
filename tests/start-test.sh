#!/bin/bash
export LANG=zh_CN.UTF-8;export LC_ALL=zh_CN.UTF-8
cd $(cd $(dirname $0) && pwd)

test -f ../env_ext.sh && \
    source ../env_ext.sh

COLOR_RED=$(    echo -e "\e[1;31;49m" )
COLOR_GREEN=$(  echo -e "\e[1;32;49m" )
COLOR_RESET=$(  echo -e "\e[0m"     )
rep_info() { echo -e "[$(date '+%F %T')] ${COLOR_GREEN}$*${COLOR_RESET}"; }
rep_error(){ echo -e "[$(date '+%F %T')] ${COLOR_RED}$*${COLOR_RESET}"; }
rep_stat() { echo -e "[$(date '+%F %T')] $*"; }

if [[ -z $1 ]];then
    r=0
    for i in `find . -maxdepth 1 -name "*.py" ! -name "__init__.py" -type f|sort`;do
        if python3 $i;then
                rep_info "Running $i success."
        else
                rep_error "Running $i failed."
            let r+=1
        fi
    done 
else
    if [[ -f $1 ]];then
        file=$1
    else
        file="test_$1"
    fi
    if python3 $file;then
        r=0
        rep_info "Running $1 success."
    else
        r=1
        rep_error "Running $1 failed."
    fi
fi

rm -f py_trpc_frame.log

if [[ $r -eq 0 ]];then
    rep_info "All interface tested success!"
    echo "Global test environment tear-down"
    echo "[  PASSED  ]"
    exit 0
else
    rep_error "Interface tested failed, plz check!"
    echo "Global test environment tear-down"
    echo "[  FAILED  ]"
    exit 1
fi

