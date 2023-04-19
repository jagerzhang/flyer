# -*- coding: utf-8 -*-
from os import environ as env
# 可开启 redis 支持
# from utils.data import RedisPool
# 可开启 MySQL 支持
# from utils.data import get_mysql_pool
# 可开启 Kafka 支持
# from utils.data import Producer
# 公共方法
from utils.common import CommonFunc as common_func  # NOQA
# 引入智研上报方法
from utils.logger import log_init
# 加强版 requests，支持异常重试、日志
from utils.http_requests import requests  # pylint: disable=unused-import
# 全局错误码
from utils import ierror  # pylint: disable=unused-import

# 主机 IP 变量
host_ip = common_func.get_host_ip()

# 日志配置
console_log_level = env.get("flyer_console_log_level", "info").upper()
file_log_level = env.get("flyer_file_log_level", "debug").upper()
logger = log_init(file_log_level, console_log_level)

logger.info("已加载环境变量如下：")
for k, v in env.items():
    logger.info(f"{k}: {v}")

# 基本配置
version = env.get("flyer_version", "v1")
base_url = env.get("flyer_base_url", "/flyer")
prefix = "%s/%s" % (base_url, version)
developer = env.get("flyer_author", "<请通过定义环境变量 flyer_author 来指定>")
# 支持显示发布日期
release_date = env.get("flyer_release_date",
                       "<请通过构建生成环境变量 flyer_release_date 来指定>")

API_TITLE = "Flyer Demo"
DESCRIPTION = f"中文名称：Flyer API 框架演示项目<br>\
功能说明：用于演示 Flyer API 开发框架的示例项目<br>\
框架源码：[Git](https://github.com/jagerzhang/flyer)<br>\
接口文档：[ReDoc]({prefix}/redoc)<br>\
快速上手：[SwaggerUI]({prefix}/docs)<br>\
技术支持：{developer}<br>\
最新发布：{release_date}"

# ============== 按需启用 ===============
# 如果启用 Redis 请取消注释
# redis_host = env.get("flyer_redis_host", "localhost")
# redis_port = env.get("flyer_redis_port", 6379)
# redis_pass = env.get("flyer_redis_pass", "")
# redis_db = env.get("flyer_redis_db", 1)
# redis_pool = RedisPool(redis_host, redis_port, redis_pass, redis_db)

# 如果启用 MySQL 请取消注释
# db_user = env.get("flyer_db_user", "root")
# db_pass = env.get("flyer_db_pass", "")
# db_host = env.get("flyer_db_host", "localhost")
# db_port = env.get("flyer_db_port", 3306)
# db_name = env.get("flyer_db_name", "fly_pigeon")
# db_recycle_rate = int(env.get("flyer_recycle_rate", 1800))
# db_pool_size = int(env.get("pigeon_db_pool_size", 32))
# db_max_overflow = int(env.get("pigeon_threads", 64))
# mysql_pool_init = get_mysql_pool(db_user, db_pass, db_host, db_port, db_name,
#                                  db_recycle_rate, db_pool_size,
#                                  db_max_overflow)
# mysql_pool = mysql_pool_init()

# 如果要用 Kafka 请自行配置：
# Kafka_topic：kafka 的 topic
# servers_list：kafka 的主机清单，逗号分隔
# producer：初始化 kafka 对象
# Kafka_topic = env.get("flyer_kafka_topic")
# servers_list = env.get("flyer_kafka_servers", "").split(",")
# producer = Producer(servers_list, Kafka_topic)
