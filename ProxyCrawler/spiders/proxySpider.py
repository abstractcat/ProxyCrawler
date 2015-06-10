# -*- coding: utf-8 -*-

__author__ = 'abstractcat'

import re

from scrapy.spider import Spider
from scrapy.spider import Request
from scrapy import Selector
import PyV8

from ProxyCrawler.items import ProxyItem

from abstractcat.db import postgres


class ProxySpider(Spider):
    def __init__(self, **kwargs):
        super(ProxySpider, self).__init__(**kwargs)
        self.db = postgres.PostgresConn()

    name = "proxy"
    allowed_domains = ['site-digger.com', 'proxy.com.ru', 'kuaidaili.com', 'baidu.com']

    def start_requests(self):
        url_sitedigger = 'http://www.site-digger.com/html/articles/20110516/proxieslist.html'
        url_proxy = 'http://www.proxy.com.ru'
        url_kuaidaili = 'http://www.kuaidaili.com/free/inha/'

        yield Request(url=url_kuaidaili, callback=self.parse_kuaidaili)
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
            (ip, port) = address.split(':')
            yield ProxyItem(ip=ip, port=port)

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
            (ip, port) = address.split(':')
            yield ProxyItem(ip=ip, port=port)

    def parse_kuaidaili(self, response):
        print(response.request.url)
        html = response.body
        html = html.replace('\n', '')
        sel = Selector(text=html)

        pattern = '<td>(\d+\.\d+\.\d+\.\d+)</td>[ ]*?<td>(\d+)</td>'
        list = re.findall(pattern, html)
        list = map(lambda x: x[0] + ':' + x[1], list)
        for address in list:
            (ip, port) = address.split(':')
            yield ProxyItem(ip=ip, port=port)

        links = response.xpath('//a[contains(@href,"/free/inha/")]/@href').extract()
        for link in links:
            link = 'http://www.kuaidaili.com' + link
            yield Request(url=link, callback=self.parse_kuaidaili)
