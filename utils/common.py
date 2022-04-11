# -*- coding: utf-8 -*-
import base64
import fcntl
import hashlib
import json
import os
import re
import socket
import binascii
import struct
import sys
from threading import Thread
from IPy import IP
from api import settings as config


class CommonFunc():
    def get_client_ip(self, request):
        """get the client IPAddress by request
        """
        try:
            real_ip = request.headers['X-Forwarded-For']
            if len(real_ip.split(',')) > 1:
                client_ip = real_ip.split(",")[0]

            else:
                client_ip = real_ip

        except Exception:  # pylint: disable=broad-except
            client_ip = request.client.host

        return client_ip

    def get_host_ip(self):
        """get the host IPAddress by socket
        """
        try:
            socket_fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_fd.connect(("www.qq.com", 80))
            host_ip = socket_fd.getsockname()[0]

        finally:
            socket_fd.close()

        return host_ip

    def get_ip_by_interface(self, ifname):
        """获取指定网卡的IP地址
        """
        ifname = ifname[:15]
        if sys.version_info.major == 3:
            ifname = bytes(ifname, "utf-8")

        socket_fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip_addr = socket.inet_ntoa(
            fcntl.ioctl(
                socket_fd.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack("256s", ifname))[20:24])
        return ip_addr

    def get_env_list(self, prefix=None, replace=True):
        """ 获取环境变量
            @ prefix： 指定目标变量的前缀
            @ replace：指定前缀后，键名是否去掉前缀
        """
        env_dict = os.environ

        if prefix:
            env_list = {}
            for key in env_dict:
                if prefix in key:
                    if replace:
                        env_list[key.replace(prefix, "")] = env_dict[key]
                    else:
                        env_list[key] = env_dict[key]

            return env_list

        else:
            return dict(env_dict)

    def filter_msg_ip(self, client_ip, default_ip):
        """ filter msg ip
        """
        # 如果客户端IP来自容器私有网络或公网代理IP，则写死一个合法IP
        inner_ip_re = r"^(9\.|11\.|30\.|100\.)"
        inner_tke_ip_re = r"^(172\.|10\.|192\.)"
        # 判断是不是内部特殊9、30、11网段IP：
        if re.match(inner_ip_re, client_ip):
            return client_ip

        # 如果是容器私有IP则使用agent_report_ip环境变量：
        elif re.match(inner_tke_ip_re, client_ip):
            return default_ip

        # 如果是公网IP则使用agent_report_ip环境变量：
        elif IP(client_ip).iptype() == 'PUBLIC':
            return default_ip

        # 否则使用客户端IP
        else:
            return client_ip

    def check_json_format(self, raw_msg):
        """
        用于判断一个字符串是否符合Json格式
        :param self:
        :return:
        """
        if isinstance(raw_msg, str):
            try:
                json.loads(raw_msg, encoding='utf-8')
            except ValueError:
                return False
            return True

        else:
            return False

    def async_func(self, func):
        """异步执行函数
        """
        def wrapper(*args, **kwargs):
            thr = Thread(target=func, args=args, kwargs=kwargs)
            thr.start()

        return wrapper

    def split_list(self, src_list, length=3, tmp_list=None):
        """列表按长度切分
        """
        if tmp_list is None:
            tmp_list = []

        if len(src_list) <= length:
            tmp_list.append(src_list)
            return tmp_list

        else:
            tmp_list.append(src_list[:length])
            return self.split_list(src_list[length:], length, tmp_list)

    def is_base64(self, string):
        """判断是不是Base64加密
        """
        try:
            if re.match(r"^b'", string):
                return base64.b64decode(string[2:-1], validate=True)

            return base64.b64decode(string, validate=True)

        except binascii.Error:
            return False

    def base64decode(self, content):
        """Base64解码，兼容不同版本客户端
        """
        resp = self.is_base64(content)

        if resp:
            return resp

        return content

    def is_ipaddress(self, address):
        """IP地址校验
        """
        try:
            IP(address)
            return True
        except Exception as error:  # pylint: disable=broad-except
            config.logger.warning(error)
            return False

    def string_to_list(self, content, length=2048, charact="utf-8"):
        """字符串按指定编码长度切分(默认UTF-8)
        """
        if charact:
            try:
                content = content.encode(charact, errors="ignore")
            except (AttributeError, UnicodeDecodeError):
                pass

        split_list = []
        for item in range(0, len(content), length):
            item_content = content[item:item + length]
            if charact:
                try:
                    item_content = item_content.decode(charact,
                                                       errors="ignore")
                except (AttributeError, UnicodeDecodeError) as error:
                    config.logger.warning(f"content decode failed: {error}")
                    pass
            split_list.append(item_content)

        return split_list

    def filter_none_item(self, src_list, verify=False):
        """去掉列表中的空元素和重复元素
        """
        if isinstance(src_list, list):
            try:
                new_list = list(set(src_list))
                new_list.sort(key=src_list.index)
                return list(filter(None, new_list))

            # 类型错误[["a","b"]]
            except TypeError:
                # 开启验证则返回错误
                if verify:
                    return False

                return src_list

        elif not src_list and verify:
            return False

        return src_list

    def hidden_secret(self, content, length=None, order=1):
        """隐藏指定长度敏感字符串
        :param  content, 原始字符串
        :paramlength，需要被替换的字符串长度，不传入时替换60%
        :paramorder，从头替换还是从尾替换，默认从尾开始替换

        """
        if not isinstance(content, str):
            return content

        if not length:
            length = int(len(content) * 0.6)
            hidden_str = "*" * length

        else:
            hidden_str = "*" * length
            length = int(len(content) - length)

        if order == 1:
            return f"{content[0:length]}{hidden_str}"

        else:
            return f"{hidden_str}{content[int(len(content) - length):]}"

    def get_md5(self, content):
        """ 计算MD5
        """
        m = hashlib.md5()
        m.update(content.encode("UTF-8"))
        return m.hexdigest()
