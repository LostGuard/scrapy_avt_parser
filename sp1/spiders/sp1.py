import scrapy
import re
import base64
from datetime import datetime
from PIL import Image
import pytesseract
import io
import json


# scrapy parse "URL" --spider --depth 2  sp1  --callback parse
class QuotesSpider(scrapy.Spider):
    name = "sp1"
    base_url = 'https://www.avito.ru'

    @staticmethod
    def get_nom(response):
        return response.css('.title-info-metadata-item:nth-child(1)::text').extract_first().split(', ')[0].split(' ')[2]

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

    @staticmethod
    def get_phone_img(response):
        re_ = response.body.decode(response.encoding)
        l = json.loads(re_)
        if 'error' in l:
            return b''
        base64_ = l['image64'].replace('data:image/png;base64,', '')
        base64_ += '=' * (4 - len(base64_) % 4)
        base64_data = str.encode(base64_)
        return base64.decodebytes(base64_data)

    @staticmethod
    def img_to_text(image_arr):
        img = Image.open(io.BytesIO(image_arr))
        txt = pytesseract.image_to_string(img)
        return txt

    def start_requests(self):
        url = 'https://www.avito.ru/kaluzhskaya_oblast/doma_dachi_kottedzhi/prodam?pmax=100000&pmin=1'
        yield scrapy.Request(url, callback=self.parse_pages)

    def parse_pages(self, response):
        print(response.css('p::text').extract())
        n = response.css('a+ .pagination-page ::attr(href)').extract_first().split('=')[1].split('&')[0]
        url = 'https://www.avito.ru/kaluzhskaya_oblast/doma_dachi_kottedzhi/prodam?p=%i&pmax=100000&pmin=1'
        for i in range(1, int(n) + 1):
            r = scrapy.Request(url % i, callback=self.parse_urls, priority=0)
            yield r

    def parse_urls(self, response):
        urls = response.css('.item-description-title-link::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(self.base_url + url, callback=self.parse, priority=0)

    def parse(self, response):
        body = response.body.decode(response.encoding)
        phone_key = re.search("avito.item.phone = '.+'", body).group(0).split(" = ")[1].replace("'", "")
        nom = self.get_nom(response)
        # https://www.avito.ru/items/phone/1196190703?pkey=abc07d22aee24d42ec7691cf59b839c1&vsrc=r
        request = scrapy.Request(
            'https://www.avito.ru/items/phone/%s?pkey=%s&vsrc=r' % (nom, self.phone_demix(nom, phone_key)),
            callback=self.parse_with_phone)
        request.meta['item'] = response
        request.priority = 500
        yield request

    def parse_with_phone(self, response):
        old_resp = response.meta['item']
        img = self.get_phone_img(response)
        print(response.body.decode(response.encoding))
        if len(img) < 20:
            print('Не корректное изображение')
            yield scrapy.Request(old_resp.url, callback=self.parse)
            return

        phone_text = self.img_to_text(img)
        rowaddr = old_resp.css('.item-map-location')
        address = rowaddr.css('.item-map-label+ span::text').extract_first() + '; ' + rowaddr.css(
            '.item-map-address span::text').extract_first().replace('\n ', '')
        nom = self.get_nom(old_resp)

        params = old_resp.css('.item-params-list-item')
        params_list = []
        for i in params:
            par1 = i.css('.item-params-label::text').extract_first()
            par2 = i.css('li.item-params-list-item::text').extract()[1].replace('\n ', '')
            params_list.append([par1, par2])

        yield {
            'url': old_resp.url,
            'title': old_resp.css('.title-info-title-text::text').extract_first(),
            'nom': nom,
            'owner': old_resp.css('.seller-info-name a::text').extract_first().replace('\n ', ''),
            'date': old_resp.css('.title-info-metadata-item:nth-child(1)::text').extract_first().split(', ')[1],
            'price': old_resp.css('.js-price-value-string::text').extract_first().replace('\n   ', ''),
            'address': address,
            'params': str(params_list),
            'description': old_resp.css('div[itemprop=description] p::text').extract_first(),
            'parsetime': datetime.now(),
            'phone': phone_text
        }
