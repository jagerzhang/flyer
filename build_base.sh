#!/bin/bash
cd $(cd $(dirname $0) && pwd)
docker build -f Dockerfile_base -t jagerzhang/flyer:base . && \
docker push jagerhang/flyer:base
