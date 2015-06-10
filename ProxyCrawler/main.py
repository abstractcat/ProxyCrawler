# -*- coding: utf-8 -*-

__author__ = 'abstractcat'

import time
import multiprocessing
from threading import Thread
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import signals
from scrapy.utils.project import get_project_settings
from spiders import proxySpider
from abstractcat.net import utils
from abstractcat.db import postgres


class CreateProxy():
    def start(self):
        while True:
            d = multiprocessing.Process(name='run', target=self.run)
            d.daemon=True
            d.start()
            d.join()

    def run(self):
        settings = get_project_settings()
        self.crawler = Crawler(settings)
        self.crawler.configure()
        self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        self.spider = proxySpider.ProxySpider()
        self.crawler.crawl(self.spider)
        self.crawler.start()
        reactor.run()


class CheckProxy(Thread):
    def __init__(self):
        super(CheckProxy, self).__init__()
        self.db = postgres.PostgresConn()

    def run(self):
        sql = 'SELECT address FROM proxy ORDER BY RANDOM() limit 1;'
        del_sql = 'DELETE FROM proxy WHERE address=\'%s\''
        while True:
            if utils.check_network_status():
                try:
                    (ip, port) = self.db.query(sql)[0][0].split(':')
                    address = ip + ':' + port
                    print 'checking for existing address:', address
                    if not utils.tcping(ip, port):
                        print 'remove existing address:', address
                        self.db.execute(del_sql % address)
                except:
                    pass
            else:
                print('network error!')
            time.sleep(1)


if __name__ == '__main__':
    CreateProxy().start()
    CheckProxy().start()
