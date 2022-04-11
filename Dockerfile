FROM jagerzhang/flyer:base
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
COPY . .
RUN sed -i "s/RELEASE_DATE/$(date '+%Y-%m-%d %H:%M')/" docker/docker-entrypoint.sh
ENTRYPOINT ["docker/docker-entrypoint.sh"]
CMD ["./run.sh"]
