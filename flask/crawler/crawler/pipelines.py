# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class AutoriaCrawlerPipeline(object):
#   def process_item(self, item, spider):
#      return item

import pymongo

from datetime import datetime
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log

class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
            if valid:
                self.collection.update(
                    {"url": item["url"]},
                    {
                        "$set": {
                            "image": item["image"],
                            "mark_name": item["mark_name"],
                            "model_name": item["model_name"],
                            "location": item["location"],
                            "price": item["price"],
                            "mileage": item["mileage"],
                            "info": item["info"],
                            "transmission": item["transmission"],
                            "fuel": item["fuel"],
                            "year": item["year"]
                        },
                        "$setOnInsert": {
                            "date": datetime.now()
                        }
                      },
                    upsert=True
                )

            #self.collection.insert(dict(item))
            log.msg("Car added to MongoDB database!",
                    level=log.DEBUG, spider=spider)
        return item
