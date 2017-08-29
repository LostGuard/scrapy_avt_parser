
import scrapy
import re
import base64
from datetime import datetime

class QuotesSpider(scrapy.Spider):
    name = "sp1"
    base_url = 'https://www.avito.ru'

    @staticmethod
    def phone_demix(avito_key, phone_key):
        result = ''
        if phone_key is None:
            return ''

        new_phone_key = ''.join(re.findall('[0-9a-f]', phone_key))

        if int(avito_key) % 2 == 0:
            new_phone_key = new_phone_key[::-1]  # reverse string

        for i in range(0, len(new_phone_key)):
            if i % 3 == 0:
                result += new_phone_key[i]
        return result



    def start_requests(self):
        url = 'https://www.avito.ru/kaluzhskaya_oblast/doma_dachi_kottedzhi/prodam?pmax=100000&pmin=1'
        yield scrapy.Request(url, callback=self.parse_pages_urls)

    def parse_pages_urls(self, response):
        print(response.css('p::text').extract())
        n = response.css('a+ .pagination-page ::attr(href)').extract_first().split('=')[1].split('&')[0]
        url = 'https://www.avito.ru/kaluzhskaya_oblast/doma_dachi_kottedzhi/prodam?p=%i&pmax=100000&pmin=1'
        for i in range(1, int(n) + 1):
            yield scrapy.Request(url % i, callback=self.parse_urls)

    def parse_urls(self, response):
        urls = response.css('.item-description-title-link::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(self.base_url + url, callback=self.parse)

    def parse(self, response):
        rowaddr = response.css('.item-map-location')
        address = rowaddr.css('.item-map-label+ span::text').extract_first() + '; ' + rowaddr.css('.item-map-address span::text').extract_first().replace('\n ', '')
        nom = response.css('.title-info-metadata-item:nth-child(1)::text').extract_first().split(', ')[0].split(' ')[2]

        params = response.css('.item-params-list-item')
        params_list = []
        for i in params:
            par1 = i.css('.item-params-label::text').extract_first()
            par2 = i.css('li.item-params-list-item::text').extract()[1].replace('\n ', '')
            params_list.append([par1, par2])

        #  -----
        body = response.body.decode(response.encoding)
        phone_key = re.search("avito.item.phone = '.+'", body).group(0).split(" = ")[1].replace("'", "")

        # https://www.avito.ru/items/phone/1196190703?pkey=abc07d22aee24d42ec7691cf59b839c1&vsrc=r
        request = scrapy.Request(
            'https://www.avito.ru/items/phone/%s?pkey=%s&vsrc=r' % (nom, self.phone_demix(nom, phone_key)),
            callback=self.parse_phone)
        request.meta['item'] = nom
        request.priority = 500
        yield request
        #  -----
        yield {
            'url': response.url,
            'title': response.css('.title-info-title-text::text').extract_first(),
            'nom': nom,
            'owner': response.css('.seller-info-name a::text').extract_first().replace('\n ', ''),
            'phone': None,
            'date': response.css('.title-info-metadata-item:nth-child(1)::text').extract_first().split(', ')[1],
            'price': response.css('.js-price-value-string::text').extract_first().replace('\n   ', ''),
            'address': address,
            'params': str(params_list),
            'description': response.css('div[itemprop=description] p::text').extract_first(),
            'parsetime': datetime.now(),
        }

    def parse_phone(self, response):
        print('GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGtghjkjgfghjklkjhgfdfghjk')
        re_ = response.body.decode(response.encoding)
        base64_ = re_.split(',')[1].replace('"}', '').replace(" '", '')
        base64_ += '=' * (4 - len(base64_) % 4)
        base64_data = str.encode(base64_)


        #print(base64_data)
        yield {
            'nom': response.meta['item'],
            'phone': base64.decodebytes(base64_data)
        }