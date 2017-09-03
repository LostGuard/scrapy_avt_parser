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
                    'nom INTEGER NOT NULL UNIQUE, owner TEXT, phone TEXT, date TEXT, price TEXT, address TEXT,'
                    'params TEXT, description TEXT, url TEXT, site TEXT, parsetime TEXT)')
        self.con.commit()

        cmd = '''DELETE FROM dom WHERE nom = ?'''
        cur.execute(cmd, (item['nom'],))

        cmd = '''INSERT INTO dom (id, title, nom, owner, phone, date, price, address, params, description, url, site, parsetime)
              VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
              '''
        cur.execute(cmd, (item['title'], item['nom'], item['owner'], item['phone'], item['date'], item['price'],
                          item['address'], item['params'], item['description'], item['url'], None, item['parsetime']))
        self.con.commit()


