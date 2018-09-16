import scrapy
import re
from flask import json
from crawler.items import CrawlerItem


class AutoBazarSpider(scrapy.Spider):
    name = "ab"


def start_requests(self):
    url = 'https://ab.ua/api/_posts/?capacity_unit=1&currency=usd&is_new=0&page=1&power_unit=1&transport=1'
    yield scrapy.Request(url=url, callback=self.parse)


def parse(self, response):
    json_response = json.loads(response.body.decode("utf-8"))

    for car in json_response["results"]:
        item = CrawlerItem()
        item["url"] = "https://ab.ua" + car["permalink"]

        item["mark_name"] = car["make"]["title"]
        item["model_name"] = car["model"]["title"]

        item["year"] = car["year"]

        for price in car["price"]:
            if price["currency"] == "usd":
                item["price"] = price["value"]
                break

        item["info"] = car["description"]
        item["mileage"] = car["mileage"]
        item["location"] = car["location"]["title"]

        item["fuel"] = ""
        item["transmission"] = ""
        if "engine" in car["characteristics"]:
            item["fuel"] = car["characteristics"]["engine"]["title"]
        if "gearbox" in car["characteristics"]:
            item["transmission"] = car["characteristics"]["gearbox"]["title"]
        if car["gas_equipment"]:
            item["fuel"] += "ГБО"

        item["image"] = ""
        if len(car["photos"]):
            item["image"] = car["photos"][0]["image"]

        if item is not None:
            yield item

    url = "https://ab.ua/api/_posts" + json_response["next"][json_response["next"].rfind("/"):]
    current_page = re.search('&page=(\d+)&', url).group(1)

    if current_page < 5:
        if url is not None:
            yield scrapy.Request(url=url, callback=self.parse)
