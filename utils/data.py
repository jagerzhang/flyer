# -*- coding: utf-8 -*-
import json
import redis
from kafka import KafkaProducer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from utils.common import CommonFunc
from api import settings as config

common_func = CommonFunc()


class RedisPool():
    """Redis 操作类
    """
    def __init__(self, host, port, passwd, database, timeout=1):
        pool = redis.ConnectionPool(host=host,
                                    port=int(port),
                                    password=passwd,
                                    db=database,
                                    decode_responses=True,
                                    socket_connect_timeout=timeout)
        self.redis_pool = redis.Redis(connection_pool=pool)

    def reconnect(self):
        """失败重连
        """
        try:
            self.close()
            return True

        except Exception as error:  # pylint: disable=broad-except

            return False

        finally:
            super(RedisPool, self).__init__()

    @common_func.async_func
    def set(self, key_name, key_value, **kwargs):
        """设置缓存键值
        """
        try:
            return self.redis_pool.set(key_name, key_value, **kwargs)

        except Exception as error:  # pylint: disable=broad-except
            config.logger.error(
                f"Redis set {key_name}:{key_value} failed: {error}")

            if self.reconnect():
                return self.redis_pool.set(key_name, key_value, **kwargs)

            else:
                return False

    def get(self, key_name):
        """获取指定缓存键的值
        """
        try:
            return self.redis_pool.get(key_name)

        except Exception as error:  # pylint: disable=broad-except
            config.logger.error(f"Redis get {key_name} failed: {error}")
            if self.reconnect():
                return self.redis_pool.get(key_name)

            else:
                return False

    @common_func.async_func
    def delete(self, key_name):
        """删除指定缓存
        """
        try:
            return self.redis_pool.delete(key_name)

        except Exception as error:  # pylint: disable=broad-except
            config.logger.error(f"Redis delete {key_name} failed: {error}")
            if self.reconnect():
                return self.redis_pool.delete(key_name)

            else:
                return False

    def ttl(self, key_name):
        """获取指定缓存键的剩余时间
        """
        try:
            return self.redis_pool.ttl(key_name)

        except Exception as error:  # pylint: disable=broad-except
            config.logger.error(f"Redis ttl {key_name} failed: {error}")
            if self.reconnect():
                return self.redis_pool.ttl(key_name)

            else:
                return False

    def close(self):
        """关闭连接
        """
        self.redis_pool.close()


def get_mysql_pool(user,
                   passwd,
                   host,
                   port,
                   database,
                   recycle_rate=1800,
                   pool_size=32,
                   max_overflow=64):
    """创建MySQl连接池
    """
    declarative_base()
    sqlalchemy_database = f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{database}"
    engine = create_engine(sqlalchemy_database,
                           pool_recycle=recycle_rate,
                           pool_size=pool_size,
                           max_overflow=max_overflow)
    return sessionmaker(autocommit=True, autoflush=True, bind=engine)


class Producer():
    """ Kafka 生产客户端
    """
    def __init__(self, servers_list, topic):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=servers_list,
            retries=5,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"))

    def send(self, msg, topic=None):
        if not topic:
            topic = self.topic

        try:
            self.producer.send(topic, msg).get(timeout=60)

        except Exception as error:  # pylint: disable=broad-except
            super(Producer, self).__init__()
            try:
                self.producer.send(topic, msg).get(timeout=60)

            except Exception as error:  # pylint: disable=broad-except
                raise Exception(error)

        return True

    def close(self):
        self.producer.close()
