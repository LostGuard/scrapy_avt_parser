# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Sp1Item(scrapy.Item):
    title = scrapy.Field()
    nom = scrapy.Field()
    owner = scrapy.Field()
    phone = scrapy.Field()
    date = scrapy.Field()
    price = scrapy.Field()
    address = scrapy.Field()
    params = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    parsetime = scrapy.Field()
