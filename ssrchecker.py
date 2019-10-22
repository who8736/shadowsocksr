from threading import Thread
from multiprocessing.dummy import Pool as ThreadPool

from time import sleep
import requests
import json
from queue import Queue

from shadowsocks.local import runClient
from shadowsocks.shell import url2dict
from config import RETRY_MAX, OK_CNT, TIMEOUT, CHECK_URL
from config import INFILENAME, OUTFILENAME, MAXTHREAD

# from shadowsocks.check import check

port_queue = Queue()
good_node_queue = Queue()

def _check(port):
    proxy = f'127.0.0.1:{port}'
    proxies = {'http': 'socks5://' + proxy,
               'https': 'socks5://' + proxy
               }

    cnt = 0
    err_cnt = 0
    # CHECK_URL = 'http://www.google.com'
    for i in range(1, RETRY_MAX + 1):
        if RETRY_MAX - err_cnt < OK_CNT:
            break
        print(f'第{i}次验证:{port}')
        try:
            response = requests.get(CHECK_URL, proxies=proxies, timeout=TIMEOUT)
            # print(response.text)
            cnt += 1
        except requests.exceptions.ConnectionError as e:
            print('Error', e.args)
            err_cnt += 1
        except requests.exceptions.ReadTimeout as e:
            print('Error', e.args)
            err_cnt += 1
        except requests.exceptions.ChunkedEncodingError as e:
            print('Error', e.args)
            err_cnt += 1

    print(f'验证{RETRY_MAX}次， 通过{cnt}次')
    if cnt >= OK_CNT:
        print('验证通过')
        return True
    else:
        print('验证失败')
        return False


def readJson():
    with open(INFILENAME, encoding='utf8') as load_f:
        configs = json.load(load_f)
        # print(configs)
        nodes = configs['configs']
        # print('nodesDict类型: ', type(nodesDict))

    nodesDict = {}
    for node in nodes:
        host = node['server']
        port = node['server_port']
        key = f'{host}:{port}'
        nodesDict[key] = node
        for k, v in node.items():
            print(k, v)
        print('=' * 20)
    # writeJson(list(nodesDict.values()))
    return list(nodesDict.values())

def writeJson(nodes):
    print('nodesDict类型: ', type(nodes))
    # configDict = {}
    with open(INFILENAME, encoding='utf8') as load_f:
        configDict = json.load(load_f)
    configDict['configs'] = nodes
    with open(OUTFILENAME, 'w') as load_f:
        json.dump(configDict, load_f)


class Checker(Thread):
    def __init__(self, ssr_text):
        Thread.__init__(self)
        self.ssr_text = ssr_text
        pass

    def run(self):
        runClient(self.ssr_text)


def fixConfig(config):
    config['server_port'] = config.get('server_port', 8388)
    config['password'] = config.get('password', b'')
    config['method'] = str(config.get('method', 'aes-256-cfb'))
    config['protocol'] = str(config.get('protocol', 'origin'))
    config['protocol_param'] = str(config.get('protocol_param', ''))
    config['obfs'] = str(config.get('obfs', 'plain'))
    config['obfs_param'] = str(config.get('obfs_param', ''))
    config['port_password'] = config.get('port_password', None)
    config['additional_ports'] = config.get('additional_ports', {})
    config['additional_ports_only'] = config.get('additional_ports_only', False)
    config['timeout'] = int(config.get('timeout', 300))
    config['udp_timeout'] = int(config.get('udp_timeout', 120))
    config['udp_cache'] = int(config.get('udp_cache', 64))
    config['fast_open'] = config.get('fast_open', False)
    config['workers'] = config.get('workers', 1)
    config['pid-file'] = config.get('pid-file', '/var/run/shadowsocksr.pid')
    config['log-file'] = config.get('log-file', '/var/log/shadowsocksr.log')
    config['verbose'] = config.get('verbose', False)
    config['connect_verbose_info'] = config.get('connect_verbose_info', 0)
    config['local_address'] = str(config.get('local_address', '127.0.0.1'))
    config['local_port'] = config.get('local_port', 1080)
    return config

def check(config):
    """
    多线程版验证主函数
    从队列中取本地可用端口，启动客户端并验证
    :param config:
    :return:
    """
    config = fixConfig(config)
    port = port_queue.get()
    config['local_port'] = port
    checker = Checker(config)
    print('启动子线程')
    checker.setDaemon(True)
    checker.start()
    sleep(3)
    print('开始验证')
    flag = _check(port)
    print('验证结果：', flag)
    port_queue.put(port)

    if flag:
        good_node_queue.put(config)


def testChecker():
    """
    测试专用
    各功能应写入相应的类或函数，本函数仅作测试或试验用
    :return:
    """

    #################################################
    # 验证单一节点是否可用
    # 用子线程启动客户端，调用验证函数
    # 该段准备放入多线程中
    ssr_text = 'ssr://NDUuMTMwLjE0NS4xNjM6ODA6YXV0aF9hZXMxMjhfbWQ1OnJjNC1tZDU6aHR0cF9zaW1wbGU6YUhSMGNEb3ZMM1F1WTI0dlJVZEtTWGx5YkEvP29iZnNwYXJhbT0mcHJvdG9wYXJhbT1kQzV0WlM5VFUxSlRWVUkmcmVtYXJrcz1VMU5TVkU5UFRGOXVkV3hzT2pRMiZncm91cD1WMWRYTGxOVFVsUlBUMHd1UTA5Tg'
    config = url2dict(ssr_text)

    config['local_port'] = config.get('local_port', 1080)
    checker = Checker(config)
    print('启动子线程')
    checker.setDaemon(True)
    checker.start()
    sleep(3)
    print('开始验证')
    flag = check()
    print('验证结果：', flag)
    #################################################


    #################################################
    # 读取配置文件中的节点，去重后存入新的配置文件
    nodes = readJson()
    print('原节点数: ', len(nodes))
    nodesDict = {}
    for node in nodes:
        host = node['server']
        port = node['server_port']
        key = f'{host}:{port}'
        nodesDict[key] = node
        for k, v in node.items():
            print(k, v)
        print('=' * 20)
    writeJson(list(nodesDict.values()))

    print('去重后节点数: ', len(nodesDict.keys()))
    #################################################

if __name__ == '__main__':
    pass
    for port in range(1080, 1090):
        port_queue.put(port)

    nodes = readJson()
    pool = ThreadPool(processes=MAXTHREAD)
    pool.map(check, nodes)
    pool.close()
    pool.join()

    # check(nodes[0])

    # while not port_queue.empty():
    #     port = port_queue.get()
    #     print(port)

    good_nodes = []
    while not good_node_queue.empty():
        node = good_node_queue.get()
        print(node)
        good_nodes.append(node)
    writeJson(good_nodes)
    print('全部验证完成！！！')

