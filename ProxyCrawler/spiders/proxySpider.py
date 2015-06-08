# -*- coding: utf-8 -*-

__author__ = 'abstractcat'

import re

from scrapy.spider import Spider
from scrapy.spider import Request
from scrapy import Selector
import PyV8

from abstractcat.db import postgres


class ProxySpider(Spider):
    def __init__(self, **kwargs):
        super(ProxySpider, self).__init__(**kwargs)
        self.db = postgres.PostgresConn()

    name = "proxy"
    allowed_domains = ['site-digger.com', 'proxy.com.ru', 'baidu.com']

    def start_requests(self):
        url_sitedigger = 'http://www.site-digger.com/html/articles/20110516/proxieslist.html'
        url_proxy = 'http://www.proxy.com.ru'

        yield Request(url=url_sitedigger, callback=self.parse_sitedigger)
        yield Request(url=url_proxy, callback=self.parse_proxy)

    def parse_proxy(self, response):
        print(response.request.url)
        html = response.body
        html = html.replace('\n', '')
        sel = Selector(text=html)

        pattern = '<td>(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)</td>'
        list = re.findall(pattern, html)
        list = map(lambda x: x[0] + ':' + x[1], list)
        for address in list:
            proxy = 'http://%s' % address
            yield Request(url='https://www.baidu.com/s?wd=%s' % address, callback=self.check_ok, errback=self.check_error,
                          meta={'proxy': proxy})

        links = response.xpath('//a/@href').extract()
        for link in links:
            link = 'http://www.proxy.com.ru/' + link
            yield Request(url=link, callback=self.parse_proxy)

    def parse_sitedigger(self, response):
        print(response.request.url)
        ctxt = PyV8.JSContext()
        ctxt.enter()

        script = open('E:/PyCharm/CatPackages/resources/js/aes.js').read()
        ctxt.eval(script)

        script = open('E:/PyCharm/CatPackages/resources/js/pad-zeropadding.js').read()
        ctxt.eval(script)

        baidu_union_id = response.xpath('//script/text()').re('var baidu_union_id = "(.*?)";')[0]
        script = 'var baidu_union_id = "%s";' % baidu_union_id
        ctxt.eval(script)

        encrypt_ips = response.xpath('//script/text()').re('document.write\(decrypt\("(.*?)"\)\)')
        for code in encrypt_ips:
            address = ctxt.eval('decrypt("%s")' % code)
            proxy = 'http://%s' % address
            yield Request(url='https://www.baidu.com/s?wd=%s' % address, callback=self.check_ok, errback=self.check_error,
                          meta={'proxy': proxy})

    def check_ok(self, response):
        query = 'SELECT * FROM proxy WHERE address=\'%s\';'
        sql = 'INSERT INTO proxy values(%s);'

        address=response.request.url.split('=')[1]
        print 'checking ok for proxy address:', address
        if self.db.query(query%address)==[]:
            self.db.execute_param(sql, (address,))

    def check_error(self, response):
        address=response.request.url.split('=')[1]
        print 'checking error for proxy address:', address
