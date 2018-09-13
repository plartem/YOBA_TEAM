# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class AutoriaCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
	
	mark_name = scrapy.Field()
	model_name = scrapy.Field()
	year = scrapy.Field()
	info = scrapy.Field() 
	url = scrapy.Field()
	price = scrapy.Field()
	mileage = scrapy.Field()
	location = scrapy.Field()
	fuel = scrapy.Field()
	transmission = scrapy.Field()
	image = scrapy.Field()
	
#    pass
