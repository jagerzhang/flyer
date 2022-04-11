FROM python:3.8-alpine3.13
LABEL maintainer="Jagerzhang<im@zhang.ge>"
LABEL description="Flyer：基于 FastAPI 的 API 开发框架."
WORKDIR /flyer
ENV flyer_host=0.0.0.0 \
    flyer_port=8080 \
    flyer_reload=True \
    flyer_report_log=False \
    flyer_log_level=debug \
    flyer_access_log=True \
    flyer_base_url=/flyer \
    flyer_version=v1

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.cloud.tencent.com/g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache make automake gcc g++ python3-dev

COPY requirements.txt /tmp/
RUN pip3 install --upgrade pip -i -i https://mirrors.cloud.tencent.com/pypi/simple  && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt -i -i https://mirrors.cloud.tencent.com/pypi/simple

COPY . .
RUN sed -i "s/RELEASE_DATE/$(date '+%Y-%m-%d %H:%M')/" docker/docker-entrypoint.sh
ENTRYPOINT ["docker/docker-entrypoint.sh"]
CMD ["./run.sh"]
