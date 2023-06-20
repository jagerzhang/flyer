#!/bin/bash

export flyer_release_date="RELEASE_DATE"

if [[ ! -z "$@" ]];then
    exec "$@"
fi
