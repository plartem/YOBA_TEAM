import scrapy
import re

from crawler.items import CrawlerItem


class RSTSpider(scrapy.Spider):
    name = "rst"
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
    start_urls = [
        'http://m.rst.ua/oldcars/?task=newresults&make%5B%5D=0&from=sform&start=1'
    ]

    def parse(self, response):

        for href in response.css('a.rst-uix-clear::attr(href)'):
            yield response.follow(href, self.parse_car)

        # follow pagination links
        href = response.css("div#rst-mobile-oldcars-results table tr td:nth-child(2) a").xpath("@href").extract_first()
        page_num = int(href[href.rfind("=") + 1:])
        if page_num <= 1:
            yield response.follow('http://m.rst.ua' + href, self.parse)

    def parse_car(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()

        item = CrawlerItem()

        href = str(response.url)

        item["url"] = href.replace('m.', '')

        item["price"] = extract_with_css("strong.rst-uix-f-right::text")

        mark_name = re.search('oldcars/(.+?)/', href).group(1)

        item["mark_name"] = mark_name

        model_name = re.search(mark_name+'/(.+?)/', href).group(1)

        item["model_name"] = model_name

        item["info"] = extract_with_css("div.rst-page-oldcars-item-option-block-container-desc::text")

        item["image"] = extract_with_css("div.rst-uix-b-item img::attr(src)")

        item["year"] = extract_with_css("a.rst-uix-black::text")

        table = response.css('table.rst-uix-table-superline')

        if len(table):

            item["location"] = response.css("td.rst-uix-left a::text")[2].extract()

            for tr in table.css("tr"):
                rows = tr.css("td")

                if len(rows) == 2:
                    if rows[0].css("::text")[0].extract() == "Топливо":
                        item["fuel"] = rows[1].css("::text")[0].extract()

                    if rows[0].css("::text")[0].extract() == "Пробег":
                        item["mileage"] = rows[1].css("::text")[0].extract()

                    if rows[0].css("::text")[0].extract() == "КПП":
                        item["transmission"] = rows[1].css("::text")[0].extract()

        else:

            list = response.css('div.rst-uix-b-item')

            for li in list.css("ul.rst-uix-list-superline li"):
                rows = li.css("li")

                if rows[0].css("::text")[1].extract() == "Топливо":
                    item["fuel"] = rows[0].css("::text")[0].extract()

                if rows[0].css("::text")[1].extract() == "Пробег":
                    item["mileage"] = rows[0].css("::text")[0].extract()

                if rows[0].css("::text")[1].extract() == "КПП":
                    item["transmission"] = rows[0].css("::text")[0].extract()

                if rows[0].css("::text")[1].extract() == "Город":
                    item["location"] = rows[0].css("::text")[0].extract()

        if item is not None:
            yield item
