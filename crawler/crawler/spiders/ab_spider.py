import scrapy
from flask import json
from scrapy.selector import Selector 
from crawler.items import CrawlerItem


class AutoriaCrawler(scrapy.Spider):
	name = "ab"
		
	def start_requests(self):
		global counter
		counter = 0
		url = 'https://ab.ua/api/_posts/?capacity_unit=1&currency=usd&is_new=0&page=1&power_unit=1&transport=1'
		yield scrapy.Request(url=url, callback=self.parse)
			
	def parse(self, response):
		global counter 
		counter += 1

		jsonresponse = json.loads(response.body_as_unicode())

		for car in jsonresponse["results"]:
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
			if hasattr(car, "characteristics"):
				item["fuel"] = car["characteristics"]["engine"]["title"]
				item["transmission"] = car["characteristics"]["gearbox"]["title"]

			if car["gas_equipment"]:
				item["fuel"] += "ГБО"

			item["image"] = ""
			if len(car["photos"]):
				item["image"] = car["photos"][0]["image"]

			if item is not None:
				yield item
						
		#self.log(name + 'has been parsed')
		
		url = jsonresponse["next"]
		
		
		if counter < 5:
			if url is not None: 
				yield scrapy.Request(url=url, callback=self.parse)
