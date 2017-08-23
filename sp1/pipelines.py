# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3 as db


class Sp1Pipeline(object):
    def open_spider(self, spider):
        self.con = db.connect('avito.db')

    def close_spider(self, spider):
        self.con.close()

    def process_item(self, item, spider):
        cur = self.con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS dom (id INTEGER PRIMARY KEY, title TEXT, '
                    'nom INTEGER, owner TEXT, phone TEXT, date TEXT, price REAL, address TEXT,'
                    'params TEXT, descr TEXT, url TEXT, site TEXT)')
        self.con.commit()

        cur.execute('''INSERT INTO dom (id, title, nom, owner, phone, date, price, address, params, descr, url, site)
                    VALUES(NULL, "%s", NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL)''' % item['title'])
        self.con.commit()
        return item
