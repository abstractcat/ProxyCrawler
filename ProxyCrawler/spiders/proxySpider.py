# -*- coding: utf-8 -*-

__author__ = 'abstractcat'

from scrapy.spider import Spider
from scrapy.spider import Request
import PyV8

from abstractcat.db import postgres


class ProxySpider(Spider):

    def __init__(self, **kwargs):
        super(ProxySpider, self).__init__(**kwargs)
        self.db = postgres.PostgresConn()

    name = "proxy"
    allowed_domains = ['site-digger.com']

    def start_requests(self):
        url_sitedigger = 'http://www.site-digger.com/html/articles/20110516/proxieslist.html'
        print(url_sitedigger)
        yield Request(url=url_sitedigger, callback=self.parse)

    # parse page with splinter
    def parse(self, response):
        query='SELECT * FROM proxy WHERE address=\'%s\';'
        sql = 'INSERT INTO proxy values(%s);'
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
            ip = ctxt.eval('decrypt("%s")' % code)
            if self.db.query(query%ip):
                continue
            self.db.execute_param(sql, (ip,))
            print(ip)
