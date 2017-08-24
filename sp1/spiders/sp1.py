
import scrapy
from datetime import datetime

class QuotesSpider(scrapy.Spider):
    name = "sp1"
    base_url = 'https://www.avito.ru'

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

        yield {
            'url': response.url,
            'title': response.css('.title-info-title-text::text').extract_first(),
            'nom': response.css('.title-info-metadata-item:nth-child(1)::text').extract_first().split(', ')[0].split(' ')[2],
            'owner': response.css('.seller-info-name a::text').extract_first().replace('\n ', ''),
            'phone': None,
            'date': response.css('.title-info-metadata-item:nth-child(1)::text').extract_first().split(', ')[1],
            'price': response.css('.js-price-value-string::text').extract_first().replace('\n   ', ''),
            'address': address,
            'params': response.css('.item-params-list-item').extract(),
            'description': str(response.css('div[itemprop=description] p::text').extract()),
            'parsetime': datetime.now(),
        }

#