# -*- coding: utf-8 -*-

__author__ = 'abstractcat'

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from scrapy.utils.project import get_project_settings

from spiders import proxySpider


def start():
    spider = proxySpider.ProxySpider()

    settings = get_project_settings()
    crawler = Crawler(settings)
    crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()
    log.start_from_crawler(crawler)
    reactor.run()


if __name__ == '__main__':
    start()
