FROM python:3.8-slim
LABEL maintainer="Jagerzhang<im@zhang.ge>"
LABEL description="Flyer：基于 FastAPI 的 API 开发框架."

WORKDIR /flyer

ENV TZ=Asia/Shanghai \
    TERM=linux \
    LANG=zh_CN.UTF-8 \
    LC_ALL=zh_CN.UTF-8 \
    flyer_host=0.0.0.0 \
    flyer_port=8080 \
    flyer_reload=1 \
    flyer_report_log=0 \
    flyer_log_level=debug \
    flyer_access_log=0 \
    flyer_base_url=/flyer \
    flyer_version=v1

RUN sed -i 's/deb.debian.org/mirrors.cloud.tencent.com/' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install make automake gcc g++ python3-dev curl default-libmysqlclient-dev net-tools -y && \
    apt-get clean

RUN pip3 install --upgrade pip && \
    pip3 install numpy protobuf Cython PyYAML aiohttp portalocker python-snappy netifaces && \
    pip3 install polaris-python log-sdk==1.0.0 rainbow-sdk>=1.1.8.5 --extra-index-url https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple


COPY requirements.txt /tmp/
RUN pip3 install --upgrade pip --index-url https://mirrors.cloud.tencent.com/pypi/simple  && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt --index-url https://mirrors.cloud.tencent.com/pypi/simple

COPY . .
RUN sed -i "s/RELEASE_DATE/$(date '+%Y-%m-%d %H:%M')/" docker/docker-entrypoint.sh
ENTRYPOINT ["docker/docker-entrypoint.sh"]
CMD ["./run.sh"]
