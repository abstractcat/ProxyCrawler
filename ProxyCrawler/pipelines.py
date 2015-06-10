# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from abstractcat.net import utils
from abstractcat.db import postgres

class ProxycrawlerPipeline(object):
    def __init__(self, **kwargs):
        super(ProxycrawlerPipeline, self).__init__(**kwargs)
        self.db = postgres.PostgresConn()

    def process_item(self, item, spider):
        ip = item['ip']
        port = item['port']

        address = ip + ':' + port
        print 'crawled address %s, checking...' % address

        query = 'SELECT * FROM proxy WHERE address=\'%s\';'
        sql = 'INSERT INTO proxy values(%s);'

        if utils.tcping(ip, port) and self.db.query(query % address) == []:
            print 'add new address:', address
            self.db.execute_param(sql, (address,))
