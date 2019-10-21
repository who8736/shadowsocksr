from threading import Thread
from time import sleep

from shadowsocks.local import runClient
from shadowsocks.check import check


class Checker(Thread):
    def __init__(self, ssr_text):
        Thread.__init__(self)
        self.ssr_text = ssr_text
        pass

    def run(self):
        runClient(self.ssr_text)


if __name__ == '__main__':
    ssr_text = 'ssr://NDUuMTMwLjE0NS4xNjM6ODA6YXV0aF9hZXMxMjhfbWQ1OnJjNC1tZDU6aHR0cF9zaW1wbGU6YUhSMGNEb3ZMM1F1WTI0dlJVZEtTWGx5YkEvP29iZnNwYXJhbT0mcHJvdG9wYXJhbT1kQzV0WlM5VFUxSlRWVUkmcmVtYXJrcz1VMU5TVkU5UFRGOXVkV3hzT2pRMiZncm91cD1WMWRYTGxOVFVsUlBUMHd1UTA5Tg'
    checker = Checker(ssr_text)
    print('启动子线程')
    checker.setDaemon(True)
    checker.start()
    sleep(3)
    print('开始验证')
    flag = check()
    print('验证结果：', flag)

