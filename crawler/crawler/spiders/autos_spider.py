import urllib.parse

import scrapy

import crawler.items as items


class AutosSpider(scrapy.Spider):
    name = 'autos_spider'
    allowed_domains = ['autos.ua']
    start_urls = ['https://autos.ua/car/']

    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 100
    }
    download_delay = 0.2

    def parse(self, response):
        for page_url in response.css('.container h3 a ::attr("href")').extract():
            yield scrapy.Request(urllib.parse.urljoin(response.url, page_url), callback=self.parse_page)

        older_page = response.css('#content  div.paging-holder  ul.page-switcher  li  a ::attr("href")').extract_first()
        if older_page is not None:
            yield scrapy.Request(urllib.parse.urljoin(response.url, older_page), callback=self.parse)

    def parse_page(self, response):
        item = items.CrawlerItem()

        self._extract_trademark_and_model(response, item)
        self._extract_year(response, item)
        self._extract_info(response, item)
        self._extract_url(response, item)
        self._extract_price(response, item)
        self._extract_mileage(response, item)
        self._extract_location(response, item)
        item['fuel'] = ''
        self._extract_transmisson(response, item)
        self._extract_image_url(response, item)

        return item

    def _extract_trademark_and_model(self, response, item):
        def process_trademark_and_model(text_arr):
            text_arr = [elem.strip('\n ') for elem in text_arr if len(elem.strip('\n ')) != 0]
            trademark, model = text_arr[0].split('(')[0].split(' ', 1)
            trademark = trademark.strip()
            model = model.strip()
            return trademark, model

        trademark, model = process_trademark_and_model(
            response.xpath('//*[@id="wrapper"]/div/div/h1/text()').extract())
        item['mark_name'] = trademark
        item['model_name'] = model

    def _extract_year(self, response, item):
        item['year'] = response.xpath(
            "//*[./text()='Год выпуска']/following-sibling::*[1]/text()").extract_first()

    def _extract_info(self, response, item):
        item['info'] = '. '.join(
            response.xpath('//*[@id="content"]/div/div[1]/div[1]/div[3]/div/div/dl/dd/text()').extract())

    def _extract_url(self, response, item):
        item['url'] = response.url

    def _extract_price(self, response, item):
        price_us = response.xpath('//*[@id="content"]/div/div[1]/div[2]/div[1]/div/strong/text()').extract_first()
        price_us = ''.join(price_us.split())

        price_uah, price_eu = response.xpath(
            '//*[@id="content"]/div/div[1]/div[2]/div[1]/strong/text()').extract_first().split('/')
        price_uah = ''.join(price_uah.split())
        price_eu = ''.join(price_eu.split())

        item['price'] = ' '.join([price_us, price_uah, price_eu])

    def _extract_mileage(self, response, item):
        item['mileage'] = response.xpath(
            "//*[./text()='Пробег (км)']/following-sibling::*[1]/text()").extract_first().replace(' ', '')

    def _extract_location(self, response, item):
        item['location'] = response.xpath(
            "//*[./text()='Город']/following-sibling::*[1]/text()").extract_first()

    def _extract_transmisson(self, response, item):
        item['transmission'] = response.xpath(
            "//*[./text()='КПП']/following-sibling::*[1]/text()").extract_first()

    def _extract_image_url(self, response, item):
        item['image'] = response.url
