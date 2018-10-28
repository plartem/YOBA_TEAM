import scrapy
from scrapy.selector import Selector 
from crawler.items import CrawlerItem


class AutoriaSpider(scrapy.Spider):
	name = "autoria"
		
	def start_requests(self):
		url = 'https://auto.ria.com/car/used/' 
		yield scrapy.Request(url=url, callback=self.parse)
			
	def parse(self, response):
			
		for car in response.css("section.ticket-item"):
			
			item = CrawlerItem()
			item["url"] = car.css("div.content").css("a.address::attr(href)").extract_first() 
				
			#item["title"] = car.css("a.address").css("span::text").extract_first() 
			
			item["mark_name"] = car.css("div.hide::attr(data-mark-name)").extract_first()
			
			item["model_name"] = car.css("div.hide::attr(data-model-name)").extract_first()
			
			item["year"] = car.css("div.hide::attr(data-year)").extract_first()
						
			item["price"] =	car.css("div.content").css("div.price-ticket::attr(data-main-price)").extract_first()
				
			item["info"] = car.css("div.definition-data").css("p").css("span::text").extract_first()

			item["mileage"] = car.css("div.definition-data").css("ul").css("li.item-char").css("li::text")[0].extract()
			
			item["location"] = car.css("div.definition-data").css("ul").css("li.item-char").css("li::text")[1].extract()
			
			item["fuel"] = car.css("div.definition-data").css("ul").css("li.item-char").css("li::text")[2].extract()
			
			item["transmission"] = car.css("div.definition-data").css("ul").css("li.item-char").css("li::text")[3].extract()
			
			item["image"] = car.css("img::attr(src)").extract_first()
			
			if item is not None:
				yield item
						
		#self.log(name + 'has been parsed')
		
		url = response.css("span.page-item.next.text-r").css("link").xpath("@href").extract_first()
		
		
		if url is not None: 
			yield scrapy.Request(url=url, callback=self.parse)
		
	
 

 
 