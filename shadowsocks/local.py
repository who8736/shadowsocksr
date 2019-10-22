#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 clowwindy
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import sys
import os
import logging
import signal


if __name__ == '__main__':
    import inspect
    file_path = os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe())))
    sys.path.insert(0, os.path.join(file_path, '../'))

from shadowsocks import shell, daemon, eventloop, tcprelay, udprelay, asyncdns
from shadowsocks.check import check


def main():
    shell.check_python()

    # fix py2exe
    if hasattr(sys, "frozen") and sys.frozen in \
            ("windows_exe", "console_exe"):
        p = os.path.dirname(os.path.abspath(sys.executable))
        os.chdir(p)

    config = shell.get_config(True)

    if not config.get('dns_ipv6', False):
        asyncdns.IPV6_CONNECTION_SUPPORT = False

    daemon.daemon_exec(config)
    logging.info("local start with protocol[%s] password [%s] method [%s] obfs [%s] obfs_param [%s]" %
            (config['protocol'], config['password'], config['method'], config['obfs'], config['obfs_param']))

    try:
        logging.info("starting local at %s:%d" %
                     (config['local_address'], config['local_port']))

        dns_resolver = asyncdns.DNSResolver()
        tcp_server = tcprelay.TCPRelay(config, dns_resolver, True)
        udp_server = udprelay.UDPRelay(config, dns_resolver, True)
        loop = eventloop.EventLoop()
        dns_resolver.add_to_loop(loop)
        tcp_server.add_to_loop(loop)
        udp_server.add_to_loop(loop)

        def handler(signum, _):
            logging.warning('received SIGQUIT, doing graceful shutting down..')
            tcp_server.close(next_tick=True)
            udp_server.close(next_tick=True)
        signal.signal(getattr(signal, 'SIGQUIT', signal.SIGTERM), handler)

        def int_handler(signum, _):
            sys.exit(1)
        signal.signal(signal.SIGINT, int_handler)

        daemon.set_user(config.get('user', None))
        loop.run()
    except Exception as e:
        shell.print_exception(e)
        sys.exit(1)

def runClient(config):
    """
    运行客户端连接到服务器
    :param config: dict, 节点参数
    :return:
    """
    # config = shell.url2dict(ssr)

    if not config.get('dns_ipv6', False):
        asyncdns.IPV6_CONNECTION_SUPPORT = False

    daemon.daemon_exec(config)
    logging.info("local start with protocol[%s] password [%s] method [%s] obfs [%s] obfs_param [%s]" %
                 (config['protocol'], config['password'], config['method'], config['obfs'], config['obfs_param']))

    try:
        logging.info("starting local at %s:%d" %
                     (config['local_address'], config['local_port']))

        dns_resolver = asyncdns.DNSResolver()
        tcp_server = tcprelay.TCPRelay(config, dns_resolver, True)
        udp_server = udprelay.UDPRelay(config, dns_resolver, True)
        loop = eventloop.EventLoop()
        dns_resolver.add_to_loop(loop)
        tcp_server.add_to_loop(loop)
        udp_server.add_to_loop(loop)

        def handler(signum, _):
            logging.warning('received SIGQUIT, doing graceful shutting down..')
            tcp_server.close(next_tick=True)
            udp_server.close(next_tick=True)
        # signal.signal(getattr(signal, 'SIGQUIT', signal.SIGTERM), handler)

        def int_handler(signum, _):
            sys.exit(1)
        # signal.signal(signal.SIGINT, int_handler)

        daemon.set_user(config.get('user', None))
        loop.run()
        # if check():
        #     print('验证完成：', ssr_text)
        #     tcp_server.close(next_tick=True)
        #     udp_server.close(next_tick=True)

    except Exception as e:
        shell.print_exception(e)
        sys.exit(1)


if __name__ == '__main__':
    # runClient()
    # main()

    # 正常服务器地址，用于验证成功的情况
    ssr_text = 'ssr://NDUuMTMwLjE0NS4xNjM6ODA6YXV0aF9hZXMxMjhfbWQ1OnJjNC1tZDU6aHR0cF9zaW1wbGU6YUhSMGNEb3ZMM1F1WTI0dlJVZEtTWGx5YkEvP29iZnNwYXJhbT0mcHJvdG9wYXJhbT1kQzV0WlM5VFUxSlRWVUkmcmVtYXJrcz1VMU5TVkU5UFRGOXVkV3hzT2pRMiZncm91cD1WMWRYTGxOVFVsUlBUMHd1UTA5Tg'
    # 无效服务器地址，用于验证失败的情况
    # ssr_text = 'ssr://c2ctYXp1cmUtMS5wdWZmdmlwLmNvbTo0NDM6YXV0aF9hZXMxMjhfbWQ1OmNoYWNoYTIwOmh0dHBfc2ltcGxlOlVHRnZablUvP29iZnNwYXJhbT0mcHJvdG9wYXJhbT1ORFEwTnprNmJrbHBTMGxDJnJlbWFya3M9VTFOU1ZFOVBURjl1ZFd4c09qTTAmZ3JvdXA9VjFkWExsTlRVbFJQVDB3dVEwOU4'
    runClient(ssr_text)
    # shell.url2dict(ssr_text)
