
import scrapy


class QuotesSpider(scrapy.Spider):
    name = "sp1"
    base_url = 'https://www.avito.ru'

    def start_requests(self):
        url = 'https://www.avito.ru/kaluzhskaya_oblast/doma_dachi_kottedzhi/prodam?pmax=100000&pmin=1'
        yield scrapy.Request(url, callback=self.parse_pages_urls)

    def parse_pages_urls(self, response):
        print('ggman!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print(response.css('p::text').extract())
        n = response.css('a+ .pagination-page ::attr(href)').extract_first().split('=')[1].split('&')[0]
        url = 'https://www.avito.ru/kaluzhskaya_oblast/doma_dachi_kottedzhi/prodam?p=%i&pmax=100000&pmin=1'
        for i in range(1, int(n)):
            yield scrapy.Request(url % i, callback=self.parse_urls)

    def parse_urls(self, response):
        urls = response.css('.item-description-title-link::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(self.base_url + url, callback=self.parse)

    def parse(self, response):
        res = response.css('p::text').extract_first()
        yield {
            'title': res,
        }

#